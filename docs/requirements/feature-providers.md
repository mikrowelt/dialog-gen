# Feature: LLM Providers

## Overview

Support for cloud LLM providers with unified interface: OpenAI API and Anthropic API.

## Supported Providers

| Provider | Type | Default Model | Status |
|----------|------|---------------|--------|
| `anthropic` | Cloud | claude-3-haiku-20240307 | Production (Default) |
| `openai` | Cloud | gpt-4o-mini | Production |

## Provider Selection Priority

1. Explicit `provider` parameter in request
2. Explicit `provider` in generator init
3. Auto-detect from model name
4. `settings.cloud.provider` default (anthropic)

## Auto-Detection Rules

| Pattern | Provider |
|---------|----------|
| `gpt-*`, `o1-*`, `chatgpt*`, `davinci*`, `text-*` | openai |
| `claude*`, `haiku`, `sonnet`, `opus` | anthropic |
| Everything else | **raises ValueError** |

## Provider-Specific Details

### OpenAI

**Endpoint**: `{cloud.openai_base_url}/chat/completions`

**Authentication**: Bearer token

**Models**:
- gpt-4o-mini (fast, cheap)
- gpt-4o (high quality)
- gpt-3.5-turbo
- o1, o1-mini

**Parameters**: temperature, top_p, max_tokens

### Anthropic

**Endpoint**: `{cloud.anthropic_base_url}/v1/messages`

**Authentication**: x-api-key header

**API Version**: 2023-06-01

**Model Normalization**:
| Input | Resolved Model |
|-------|----------------|
| `haiku`, `claude-haiku` | claude-3-haiku-20240307 |
| `sonnet`, `claude-sonnet` | claude-sonnet-4-20250514 |
| `opus`, `claude-opus` | claude-opus-4-20250514 |

**Parameters**: temperature, max_tokens (no top_p)

## CLI Usage

```bash
# Explicit provider
dialog-gen generate -n "FoodBox" -d "delivery" -p anthropic -m haiku

# Auto-detect from model
dialog-gen generate -n "FoodBox" -d "delivery" -m gpt-4o-mini

# List models by provider
dialog-gen models -p anthropic
```

## API Usage

```json
{
  "subject": {...},
  "model": "haiku",
  "num_turns": 4
}
```

Provider auto-detected from model name.

## Error Handling

| Error | Handling |
|-------|----------|
| Missing API key | ValueError with clear message |
| Unknown model/provider | ValueError with supported providers list |
| Rate limit | Propagate error to caller |
| Network error | Timeout after 120s |

## Code Reference (ast-grep)

### Classes
- `class CloudClient` - OpenAI/Anthropic cloud client

### Key Functions
- `def detect_provider(model: str) -> str` - Shared provider detection (in `utils.py`)
- `async def generate($$$) -> str` - Generate text from prompt
- `def get_cloud_client() -> CloudClient` - Singleton accessor
- `def reset_cloud_client() -> None` - Reset for testing/config reload
- `async def _generate_openai($$$) -> str` - OpenAI API call
- `async def _generate_anthropic($$$) -> str` - Anthropic API call
- `async def list_models($$$) -> list` - List available models

### Singleton Instances
- `cloud_client` - Global CloudClient instance (lazy-loaded)

## Verification Criteria

- [x] OpenAI generation works with valid key
- [x] Anthropic generation works with valid key
- [x] Auto-detection selects correct provider
- [x] Unknown models raise ValueError
- [x] Missing API key gives clear error
- [x] Model normalization works (haiku -> full name)

## Related

- [Configuration](./feature-configuration.md)
- [Provider Architecture](../architecture/providers.md)
- [Utilities Architecture](../architecture/utils.md) - Shared `detect_provider()` function
