"""
Cloud LLM client for OpenAI and Anthropic APIs.

Provides a unified interface for cloud-based language models as an
alternative to local Ollama models.
"""

import httpx
from typing import Optional

from .utils import detect_provider


class CloudClient:
    """Client for cloud LLM APIs (OpenAI, Anthropic).

    Supports OpenAI and Anthropic APIs with a unified interface
    that matches the OllamaClient for easy swapping.

    Attributes:
        openai_api_key: API key for OpenAI.
        anthropic_api_key: API key for Anthropic.
        openai_base_url: OpenAI API base URL.
        anthropic_base_url: Anthropic API base URL.
        timeout: Request timeout in seconds.

    Example:
        >>> client = CloudClient(openai_api_key="sk-...")
        >>> response = await client.generate(
        ...     model="gpt-4o-mini",
        ...     prompt="Write a greeting",
        ...     provider="openai"
        ... )
    """

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        openai_base_url: str = "https://api.openai.com/v1",
        anthropic_base_url: str = "https://api.anthropic.com",
        timeout: float = 120.0
    ):
        """Initialize cloud client.

        Args:
            openai_api_key: OpenAI API key.
            anthropic_api_key: Anthropic API key.
            openai_base_url: OpenAI API base URL.
            anthropic_base_url: Anthropic API base URL.
            timeout: Request timeout in seconds.
        """
        self.openai_api_key = openai_api_key
        self.anthropic_api_key = anthropic_api_key
        self.openai_base_url = openai_base_url.rstrip("/")
        self.anthropic_base_url = anthropic_base_url.rstrip("/")
        self.timeout = timeout

    def _detect_provider(self, model: str) -> str:
        """Detect provider from model name.

        Args:
            model: Model name.

        Returns:
            Provider name: 'openai', 'anthropic', or 'ollama'.
        """
        return detect_provider(model)

    async def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.8,
        top_p: float = 0.9,
        max_tokens: int = 2048,
        provider: Optional[str] = None
    ) -> str:
        """Generate text using cloud LLM.

        Args:
            model: Model name.
            prompt: User prompt.
            system: System prompt.
            temperature: Sampling temperature.
            top_p: Nucleus sampling parameter.
            max_tokens: Maximum tokens to generate.
            provider: Force provider ('openai' or 'anthropic').

        Returns:
            Generated text.

        Raises:
            ValueError: If API key not configured for provider.
            httpx.HTTPStatusError: On API errors.
        """
        provider = provider or self._detect_provider(model)

        if provider == "openai":
            return await self._generate_openai(
                model, prompt, system, temperature, top_p, max_tokens
            )
        elif provider == "anthropic":
            return await self._generate_anthropic(
                model, prompt, system, temperature, top_p, max_tokens
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")

    async def _generate_openai(
        self,
        model: str,
        prompt: str,
        system: Optional[str],
        temperature: float,
        top_p: float,
        max_tokens: int
    ) -> str:
        """Generate using OpenAI API.

        Args:
            model: Model name (e.g., 'gpt-4o-mini').
            prompt: User prompt.
            system: System prompt.
            temperature: Temperature.
            top_p: Top-p sampling.
            max_tokens: Max tokens.

        Returns:
            Generated text.
        """
        if not self.openai_api_key:
            raise ValueError(
                "OpenAI API key not configured. "
                "Set DIALOG_GEN_OPENAI_API_KEY environment variable or "
                "configure via 'dialog-gen config set cloud.openai_api_key <key>'"
            )

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.openai_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "top_p": top_p,
                    "max_tokens": max_tokens
                }
            )
            response.raise_for_status()
            data = response.json()

        return data["choices"][0]["message"]["content"]

    async def _generate_anthropic(
        self,
        model: str,
        prompt: str,
        system: Optional[str],
        temperature: float,
        top_p: float,
        max_tokens: int
    ) -> str:
        """Generate using Anthropic API.

        Args:
            model: Model name (e.g., 'claude-3-haiku-20240307').
            prompt: User prompt.
            system: System prompt.
            temperature: Temperature.
            top_p: Top-p sampling.
            max_tokens: Max tokens.

        Returns:
            Generated text.
        """
        if not self.anthropic_api_key:
            raise ValueError(
                "Anthropic API key not configured. "
                "Set DIALOG_GEN_ANTHROPIC_API_KEY environment variable or "
                "configure via 'dialog-gen config set cloud.anthropic_api_key <key>'"
            )

        # Normalize model names
        if model == "claude-haiku" or model == "haiku":
            model = "claude-3-haiku-20240307"
        elif model == "claude-sonnet" or model == "sonnet":
            model = "claude-sonnet-4-20250514"
        elif model == "claude-opus" or model == "opus":
            model = "claude-opus-4-20250514"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            payload = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}]
            }

            if system:
                payload["system"] = system

            # Note: Anthropic doesn't use top_p exactly like OpenAI
            # Using temperature only for simplicity
            if temperature != 1.0:
                payload["temperature"] = temperature

            response = await client.post(
                f"{self.anthropic_base_url}/v1/messages",
                headers={
                    "x-api-key": self.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            response.raise_for_status()
            data = response.json()

        return data["content"][0]["text"]

    async def list_models(self, provider: str = "openai") -> list[str]:
        """List available models.

        Args:
            provider: Provider to list models for.

        Returns:
            List of model names.
        """
        if provider == "openai":
            if not self.openai_api_key:
                return []

            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(
                    f"{self.openai_base_url}/models",
                    headers={"Authorization": f"Bearer {self.openai_api_key}"}
                )
                if response.status_code != 200:
                    return []
                data = response.json()

            # Filter to chat models
            return sorted([
                m["id"] for m in data.get("data", [])
                if any(x in m["id"] for x in ["gpt-", "o1-"])
            ])

        elif provider == "anthropic":
            # Anthropic doesn't have a models endpoint, return known models
            return [
                "claude-3-haiku-20240307",
                "claude-3-5-haiku-20241022",
                "claude-3-5-sonnet-20241022",
                "claude-sonnet-4-20250514",
                "claude-opus-4-20250514"
            ]

        return []


# Singleton instance will be created after settings are loaded
cloud_client: Optional[CloudClient] = None


def get_cloud_client() -> CloudClient:
    """Get or create cloud client singleton.

    Returns:
        CloudClient instance.
    """
    global cloud_client

    if cloud_client is None:
        from .settings import settings
        cloud_client = CloudClient(
            openai_api_key=settings.cloud.openai_api_key,
            anthropic_api_key=settings.cloud.anthropic_api_key,
            openai_base_url=settings.cloud.openai_base_url,
            anthropic_base_url=settings.cloud.anthropic_base_url
        )

    return cloud_client


def reset_cloud_client() -> None:
    """Reset cloud client singleton (for testing or config reload)."""
    global cloud_client
    cloud_client = None
