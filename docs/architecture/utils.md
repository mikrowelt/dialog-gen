# Utilities Module

## Overview

`utils.py` contains shared utility functions used across multiple modules in dialog-gen. Created to consolidate duplicate implementations and maintain DRY principles.

## Location

`src/dialog_gen/utils.py`

## Functions

### detect_provider()

```python
def detect_provider(model: str) -> str:
```

Detects the LLM provider from a model name string.

**Arguments:**
- `model`: Model name to detect provider for (e.g., "gpt-4o-mini", "claude-3-haiku", "hermes3:8b")

**Returns:**
- `str`: Provider name - one of: `"openai"`, `"anthropic"`, `"ollama"`

**Detection Rules:**

| Pattern | Provider |
|---------|----------|
| `gpt-*`, `o1-*`, `chatgpt*`, `davinci*`, `text-*` | `openai` |
| `claude*`, `haiku`, `sonnet`, `opus` | `anthropic` |
| Everything else | `ollama` |

**Usage:**

```python
from dialog_gen.utils import detect_provider

# OpenAI models
detect_provider("gpt-4o-mini")      # -> "openai"
detect_provider("o1-preview")        # -> "openai"

# Anthropic models
detect_provider("claude-3-haiku")    # -> "anthropic"
detect_provider("haiku")             # -> "anthropic"
detect_provider("sonnet")            # -> "anthropic"

# Local Ollama models (default)
detect_provider("hermes3:8b")        # -> "ollama"
detect_provider("llama3:8b")         # -> "ollama"
```

**Consumers:**

| Module | Usage |
|--------|-------|
| `generator.py` | `DialogGenerator._detect_provider()` delegates to this |
| `cloud_client.py` | `CloudClient._detect_provider()` delegates to this |
| `cli.py` | Auto-detect provider in `generate` and `compare` commands |

## ast-grep Patterns

```python
# Find the function definition
"def detect_provider($$$)"

# Find usages
"detect_provider($$$)"

# Find imports
"from .utils import detect_provider"
```

## Design Decision

This module was created during refactoring to consolidate duplicate `detect_provider` implementations that existed in:
- `cli.py` (local function)
- `cloud_client.py` (`CloudClient._detect_provider` method)
- `generator.py` (`DialogGenerator._detect_provider` method)

All now delegate to the shared `utils.detect_provider()` function.

## Related

- [Generator Architecture](./generator.md)
- [Providers Architecture](./providers.md)
- [LLM Providers Feature](../requirements/feature-providers.md)
