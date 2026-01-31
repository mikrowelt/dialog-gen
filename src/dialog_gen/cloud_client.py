"""
Cloud LLM client for OpenRouter API.

Provides a unified interface for cloud-based language models
via OpenRouter.
"""

import httpx
from typing import Optional


class CloudClient:
    """Client for OpenRouter cloud LLM API.

    Attributes:
        openrouter_api_key: API key for OpenRouter.
        openrouter_base_url: OpenRouter API base URL.
        timeout: Request timeout in seconds.

    Example:
        >>> client = CloudClient(openrouter_api_key="sk-or-...")
        >>> response = await client.generate(
        ...     model="anthropic/claude-3-haiku-20240307",
        ...     prompt="Write a greeting",
        ... )
    """

    def __init__(
        self,
        openrouter_api_key: Optional[str] = None,
        openrouter_base_url: str = "https://openrouter.ai/api/v1",
        timeout: float = 120.0
    ):
        """Initialize cloud client.

        Args:
            openrouter_api_key: OpenRouter API key.
            openrouter_base_url: OpenRouter API base URL.
            timeout: Request timeout in seconds.
        """
        self.openrouter_api_key = openrouter_api_key
        self.openrouter_base_url = openrouter_base_url.rstrip("/")
        self.timeout = timeout

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
        """Generate text using OpenRouter.

        Args:
            model: Model name (e.g., 'anthropic/claude-3-haiku-20240307').
            prompt: User prompt.
            system: System prompt.
            temperature: Sampling temperature.
            top_p: Nucleus sampling parameter.
            max_tokens: Maximum tokens to generate.
            provider: Ignored, kept for backward compatibility.

        Returns:
            Generated text.

        Raises:
            ValueError: If API key not configured.
            httpx.HTTPStatusError: On API errors.
        """
        return await self._generate_openrouter(
            model, prompt, system, temperature, top_p, max_tokens
        )

    async def _generate_openrouter(
        self,
        model: str,
        prompt: str,
        system: Optional[str],
        temperature: float,
        top_p: float,
        max_tokens: int
    ) -> str:
        """Generate using OpenRouter API.

        Args:
            model: Model name (e.g., 'anthropic/claude-3-haiku-20240307').
            prompt: User prompt.
            system: System prompt.
            temperature: Temperature.
            top_p: Top-p sampling.
            max_tokens: Max tokens.

        Returns:
            Generated text.
        """
        if not self.openrouter_api_key:
            raise ValueError(
                "OpenRouter API key not configured. "
                "Set DIALOG_GEN_OPENROUTER_API_KEY environment variable or "
                "configure via 'dialog-gen config set cloud.openrouter_api_key <key>'"
            )

        # Auto-prefix bare Claude model names with 'anthropic/'
        if not "/" in model:
            if model.startswith("claude") or model in ("haiku", "sonnet", "opus"):
                # Normalize short aliases
                if model == "haiku":
                    model = "anthropic/claude-3-haiku-20240307"
                elif model == "sonnet":
                    model = "anthropic/claude-sonnet-4-20250514"
                elif model == "opus":
                    model = "anthropic/claude-opus-4-20250514"
                else:
                    model = f"anthropic/{model}"

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.openrouter_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/mikrowelt/dialog-gen",
                    "X-Title": "dialog-gen",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "top_p": top_p,
                    "max_tokens": max_tokens,
                }
            )
            response.raise_for_status()
            data = response.json()

        return data["choices"][0]["message"]["content"]

    async def list_models(self) -> list[str]:
        """List available models via OpenRouter.

        Returns:
            List of model names.
        """
        return [
            "anthropic/claude-3-haiku-20240307",
            "anthropic/claude-3-5-haiku-20241022",
            "anthropic/claude-3-5-sonnet-20241022",
            "anthropic/claude-sonnet-4-20250514",
            "anthropic/claude-opus-4-20250514",
        ]


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
            openrouter_api_key=settings.cloud.openrouter_api_key,
            openrouter_base_url=settings.cloud.openrouter_base_url,
        )

    return cloud_client


def reset_cloud_client() -> None:
    """Reset cloud client singleton (for testing or config reload)."""
    global cloud_client
    cloud_client = None
