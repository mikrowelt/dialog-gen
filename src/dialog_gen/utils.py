"""Shared utilities for dialog generation."""


def detect_provider(model: str) -> str:
    """Detect provider from model name.

    Args:
        model: Model name to detect provider for.

    Returns:
        Provider name: 'openai', 'anthropic', or 'ollama'.

    Examples:
        >>> detect_provider("gpt-4o-mini")
        'openai'
        >>> detect_provider("claude-3-haiku")
        'anthropic'
        >>> detect_provider("hermes3:8b")
        'ollama'
    """
    model_lower = model.lower()

    # OpenAI models
    if any(m in model_lower for m in ["gpt-", "o1-", "chatgpt", "davinci", "text-"]):
        return "openai"

    # Anthropic models
    if any(m in model_lower for m in ["claude", "haiku", "sonnet", "opus"]):
        return "anthropic"

    # Default to ollama for local models
    return "ollama"
