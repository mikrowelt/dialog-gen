# LLM Providers Architecture

## Overview

Two client implementations provide access to local and cloud LLMs:
- `OllamaClient` (`ollama_client.py`) - Local Ollama server
- `CloudClient` (`cloud_client.py`) - OpenAI and Anthropic APIs

## OllamaClient

### Singleton Pattern

```python
ollama = OllamaClient()  # Global instance
```

### Class Structure

```python
class OllamaClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.api.ollama_url
        self._client: Optional[httpx.AsyncClient] = None
```

### Methods

#### list_models() → list[ModelInfo]
- Endpoint: `GET /api/tags`
- Returns formatted model info with human-readable sizes

#### generate()
```python
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
```
- Endpoint: `POST /api/generate`
- Maps `max_tokens` → `num_predict` (Ollama naming)

#### chat()
```python
async def chat(
    self,
    model: str,
    messages: list[dict],
    system: Optional[str] = None,
    ...
) -> str:
```
- Endpoint: `POST /api/chat`
- Messages format: `[{role, content}, ...]`

#### pull_model() → AsyncIterator[dict]
- Endpoint: `POST /api/pull`
- Streaming response for progress updates

#### model_exists() → bool
- Checks if model available locally

### Connection Management

- Lazy client initialization
- 300s timeout
- `close()` for cleanup

## CloudClient

### Imports

```python
from .utils import detect_provider
```

### Singleton Pattern

```python
cloud_client: Optional[CloudClient] = None

def get_cloud_client() -> CloudClient:
    # Lazy initialization from settings

def reset_cloud_client() -> None:
    # Reset for testing/config reload
```

### Class Structure

```python
class CloudClient:
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        openai_base_url: str = "https://api.openai.com/v1",
        anthropic_base_url: str = "https://api.anthropic.com",
        timeout: float = 120.0
    ):
```

### Unified Interface

```python
async def generate(
    self,
    model: str,
    prompt: str,
    system: Optional[str] = None,
    temperature: float = 0.8,
    top_p: float = 0.9,
    max_tokens: int = 2048,
    provider: Optional[str] = None  # Auto-detect if None
) -> str:
```

Routes to appropriate provider method.

### OpenAI Implementation

```python
async def _generate_openai(...) -> str:
```

**Request**:
```json
POST {openai_base_url}/chat/completions
Authorization: Bearer {api_key}

{
  "model": "gpt-4o-mini",
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
  ],
  "temperature": 0.8,
  "top_p": 0.9,
  "max_tokens": 2048
}
```

**Response**: `data["choices"][0]["message"]["content"]`

### Anthropic Implementation

```python
async def _generate_anthropic(...) -> str:
```

**Model Normalization**:
| Input | Output |
|-------|--------|
| `haiku` | `claude-3-haiku-20240307` |
| `sonnet` | `claude-sonnet-4-20250514` |
| `opus` | `claude-opus-4-20250514` |

**Request**:
```json
POST {anthropic_base_url}/v1/messages
x-api-key: {api_key}
anthropic-version: 2023-06-01

{
  "model": "claude-3-haiku-20240307",
  "system": "...",
  "messages": [{"role": "user", "content": "..."}],
  "temperature": 0.8,
  "max_tokens": 2048
}
```

**Response**: `data["content"][0]["text"]`

**Note**: Anthropic API doesn't support `top_p`.

### Provider Detection

```python
def _detect_provider(self, model: str) -> str:
    """Delegates to shared utils.detect_provider()"""
    return detect_provider(model)
```

Uses the shared `detect_provider()` function from `utils.py`. See [Utilities](./utils.md) for details.

| Pattern | Provider |
|---------|----------|
| `gpt-*`, `o1-*`, `chatgpt*`, `davinci*`, `text-*` | openai |
| `claude*`, `haiku`, `sonnet`, `opus` | anthropic |
| default | ollama |

### list_models()

- **OpenAI**: Calls `/models` endpoint, filters to GPT/O1 models
- **Anthropic**: Returns hardcoded list (no API for listing)

## Error Handling

| Error | Handling |
|-------|----------|
| Missing API key | `ValueError` with clear message |
| HTTP 401 | Invalid API key |
| HTTP 429 | Rate limited |
| HTTP 5xx | Server error |
| Timeout | 120s default |

## Configuration Integration

```python
# From settings
openai_api_key = settings.cloud.openai_api_key
anthropic_api_key = settings.cloud.anthropic_api_key
openai_base_url = settings.cloud.openai_base_url
anthropic_base_url = settings.cloud.anthropic_base_url
```

## Related

- [Utilities](./utils.md) - Shared `detect_provider()` function
- [LLM Providers Feature](../requirements/feature-providers.md)
- [Configuration Feature](../requirements/feature-configuration.md)
