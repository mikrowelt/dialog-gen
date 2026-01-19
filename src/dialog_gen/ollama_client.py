"""
Ollama API client wrapper.

Provides async interface for interacting with a local Ollama server
for LLM generation tasks.
"""

import json
import httpx
from typing import AsyncIterator, Optional

from .settings import settings
from .models import ModelInfo


class OllamaClient:
    """Async client for Ollama API.

    Handles all communication with the Ollama server including
    model listing, text generation, and model management.

    Attributes:
        base_url: Ollama server URL.

    Example:
        >>> client = OllamaClient()
        >>> models = await client.list_models()
        >>> response = await client.generate("hermes3:8b", "Hello!")
    """

    def __init__(self, base_url: Optional[str] = None):
        """Initialize the client.

        Args:
            base_url: Ollama server URL. Defaults to settings.api.ollama_url.
        """
        self.base_url = base_url or settings.api.ollama_url
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(300.0, connect=10.0)
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def list_models(self) -> list[ModelInfo]:
        """List available models.

        Returns:
            List of ModelInfo objects for each installed model.
        """
        client = await self._get_client()
        resp = await client.get("/api/tags")
        resp.raise_for_status()
        data = resp.json()
        return [
            ModelInfo(
                name=m["name"],
                size=self._format_size(m.get("size", 0)),
                modified_at=m.get("modified_at"),
                digest=m.get("digest", "")[:12]
            )
            for m in data.get("models", [])
        ]

    async def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str:
        """Generate completion from model.

        Args:
            model: Model name to use.
            prompt: User prompt text.
            system: Optional system prompt.
            temperature: Creativity (0-2). Defaults to settings value.
            top_p: Nucleus sampling. Defaults to settings value.
            max_tokens: Max output length. Defaults to settings value.
            stream: Whether to stream response.

        Returns:
            Generated text response.
        """
        client = await self._get_client()

        # Use settings defaults
        temperature = temperature if temperature is not None else settings.generation.temperature
        top_p = top_p if top_p is not None else settings.generation.top_p
        max_tokens = max_tokens if max_tokens is not None else settings.generation.max_tokens

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "num_predict": max_tokens,
            }
        }

        if system:
            payload["system"] = system

        resp = await client.post("/api/generate", json=payload)
        resp.raise_for_status()
        return resp.json()["response"]

    async def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Chat completion with message history.

        Args:
            model: Model name to use.
            messages: List of message dicts with 'role' and 'content'.
            system: Optional system prompt.
            temperature: Creativity (0-2).
            top_p: Nucleus sampling.
            max_tokens: Max output length.

        Returns:
            Assistant response text.
        """
        client = await self._get_client()

        # Use settings defaults
        temperature = temperature if temperature is not None else settings.generation.temperature
        top_p = top_p if top_p is not None else settings.generation.top_p
        max_tokens = max_tokens if max_tokens is not None else settings.generation.max_tokens

        chat_messages = []
        if system:
            chat_messages.append({"role": "system", "content": system})
        chat_messages.extend(messages)

        payload = {
            "model": model,
            "messages": chat_messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "num_predict": max_tokens,
            }
        }

        resp = await client.post("/api/chat", json=payload)
        resp.raise_for_status()
        return resp.json()["message"]["content"]

    async def pull_model(self, model: str) -> AsyncIterator[dict]:
        """Pull a model with progress updates.

        Args:
            model: Model name to pull.

        Yields:
            Progress update dicts with 'status' field.
        """
        client = await self._get_client()

        async with client.stream("POST", "/api/pull", json={"name": model}) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if line:
                    yield json.loads(line)

    async def model_exists(self, model: str) -> bool:
        """Check if model is available locally.

        Args:
            model: Model name to check.

        Returns:
            True if model is installed.
        """
        models = await self.list_models()
        model_names = [m.name.split(":")[0] for m in models]
        return model.split(":")[0] in model_names

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format bytes to human readable string."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f}TB"


# Global client instance
ollama = OllamaClient()
