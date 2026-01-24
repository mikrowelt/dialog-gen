# Generator Architecture

## Overview

`DialogGenerator` is the core engine that orchestrates dialog generation across multiple LLM providers. Located in `src/dialog_gen/generator.py`.

## Imports

```python
from .utils import detect_provider
from .ollama_client import ollama
from .cloud_client import get_cloud_client
from .settings import settings
from .models import Subject, Brand, Campaign, DialogContext, DialogMessage, GeneratedDialog, GenerateRequest, SingleResponseRequest
```

## Class: DialogGenerator

### Initialization

```python
def __init__(
    self,
    model: Optional[str] = None,
    provider: Optional[str] = None
):
```

- `model`: LLM model name (default: from settings)
- `provider`: "ollama", "openai", "anthropic", or "auto"

### Provider Resolution

```
1. Explicit provider param → use it
2. provider="auto" or None:
   - Detect from model name via _detect_provider()
   - OpenAI patterns: gpt-*, o1-*, chatgpt*, davinci*, text-*
   - Anthropic patterns: claude*, haiku, sonnet, opus
   - Default: ollama
3. If still None: settings.cloud.provider
```

**Note:** `_detect_provider()` method delegates to the shared `detect_provider()` function from `utils.py`. See [Utilities](./utils.md).

## Public Methods

### generate_dialog()

```python
async def generate_dialog(
    self,
    request: GenerateRequest
) -> GeneratedDialog:
```

**Flow**:
1. Build system prompt from subject/campaign/language
2. Build generation prompt with context
3. Call LLM via appropriate provider
4. Parse dialog output (JSON or text)
5. Calculate typing delays
6. Return GeneratedDialog with metadata

### generate_single_response()

```python
async def generate_single_response(
    self,
    request: SingleResponseRequest
) -> DialogMessage:
```

For interactive sessions - generates single next message.

## Private Methods

### _build_system_prompt()

```python
def _build_system_prompt(
    self,
    subject: Subject,
    campaign: Campaign,
    language: str
) -> str:
```

**Russian prompt structure**:
```
{system_prefix}

{TYPE_LABEL} для упоминания: {name} ({description})
Особенности/Ключевые моменты: {attributes}
Контекст: {context_hint}
НЕ упоминай: {constraints}

{style_rules}
{negative_examples}
{mention_instruction}
```

**English prompt structure**:
```
{system_prefix}

{TYPE_LABEL}: {name}
What it is: {description}
Features/Key points: {attributes}
Context: {context_hint}
Promo code: {promo_code} ({promo_benefit})
DO NOT mention: {constraints}

GOAL: {campaign.goal}
STYLE: {campaign.style}
HOW TO MENTION: {campaign.mention_type}

{style_rules}
```

### _build_generation_prompt()

```python
def _build_generation_prompt(
    self,
    subject: Subject,
    campaign: Campaign,
    num_turns: int,
    context: Optional[DialogContext],
    language: str
) -> str:
```

**With context (Russian)**:
- Shows last 10 messages
- Calculates avg/max message length
- Enforces length constraints
- Includes mention instruction

**Without context**:
- Simple instruction to generate messages
- JSON output format

### _call_llm()

```python
async def _call_llm(
    self,
    model: str,
    prompt: str,
    system: str,
    temperature: float,
    provider: str
) -> str:
```

**Routing**:
- "openai" / "anthropic" → `get_cloud_client().generate()`
- Default → `ollama.generate()`

### _parse_dialog()

```python
def _parse_dialog(
    self,
    raw_text: str
) -> list[DialogMessage]:
```

**Parsing strategy**:
1. Extract JSON array from text
2. Handle common LLM errors:
   - Trailing commas
   - Escaped newlines
   - Various field names (role/sender/responder, text/content/message)
3. Normalize roles (sender→person1, responder→person2)
4. Skip placeholder text
5. Fallback to line-by-line parsing

### _parse_dialog_lines()

Fallback parser for non-JSON output:
- Regex for embedded JSON objects
- Line-by-line with `role: content` format
- Cyclic role assignment

### _calculate_delay()

```python
def _calculate_delay(
    self,
    message: DialogMessage
) -> float:
```

**Formula**: `word_count * 1.5 * random(0.8, 1.2)`

**Constraints**: max 30 seconds

## Error Handling

| Scenario | Handling |
|----------|----------|
| JSON parse failure | Fallback to line parser |
| Empty response | Return empty message list |
| Provider error | Propagate to caller |
| Invalid model | HTTP 400/404 |

## Performance Considerations

- Async I/O for LLM calls
- Single HTTP client per provider (connection reuse)
- Timeout: 120s default
- Progress indicators in CLI

## Related

- [Data Model](./data-model.md)
- [Providers](./providers.md)
- [Utilities](./utils.md) - Shared `detect_provider()` function
- [Dialog Generation Feature](../requirements/feature-dialog-generation.md)
