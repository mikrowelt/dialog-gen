# Data Model Architecture

## Overview

All data models use Pydantic v2 for validation, serialization, and documentation. Located in `src/dialog_gen/models.py`.

## Core Models

### Subject

Primary model for anything to be mentioned in dialogs.

```python
class Subject(BaseModel):
    name: str                           # Required
    description: str                    # Required
    type: str = "brand"                 # brand|product|service|topic|info|event
    attributes: list[str] = []          # Key points
    constraints: list[str] = []         # What NOT to mention
    mention_style: str = "natural"      # natural|casual|enthusiastic|skeptical
    context_hint: Optional[str] = None  # Extra LLM context
    promo: Optional[dict] = None        # {code, benefit}
```

**Methods**:
- `get_type_label(language)` → Localized type label
- `get_mention_instruction(language)` → Localized instruction

**Properties** (backward compat):
- `what_is_it` → `description`
- `features` → `attributes`
- `do_not_mention` → `constraints`
- `promo_code` → `promo.get("code")`
- `promo_benefit` → `promo.get("benefit")`
- `topic` → `context_hint`

### Brand (Factory Function)

```python
def Brand(
    name: str,
    what_is_it: Optional[str] = None,
    description: Optional[str] = None,
    # ... legacy and new fields
) -> Subject:
```

Creates `Subject` with `type="brand"`, maps legacy fields.

### Campaign

```python
class Campaign(BaseModel):
    goal: str = "awareness"         # awareness|engagement|information|trial|conversion
    style: str = "casual"           # casual|enthusiastic|skeptical|curious
    mention_type: str = "natural"   # natural|recommendation|personal_experience|question
    include_promo: bool = False
    urgency: bool = False
```

**Validator**: Maps `brand_mention_type` → `mention_type`.

### DialogContext

```python
class DialogContext(BaseModel):
    messages: list[dict[str, str]] = []  # [{role, content}]
    topic: Optional[str] = None
    setting: Optional[str] = None
```

### DialogMessage

```python
class DialogMessage(BaseModel):
    role: str                            # person1, person2, etc.
    content: str
    delay_hint: Optional[float] = None   # Seconds
```

### GeneratedDialog

```python
class GeneratedDialog(BaseModel):
    messages: list[DialogMessage]
    model_used: str
    generation_params: dict  # provider, temperature, timing, etc.
```

## Request Models

All request models inherit from `_SubjectRequestMixin`:

```python
class _SubjectRequestMixin:
    @model_validator(mode="before")
    def handle_brand_alias(cls, data):
        # Maps brand → subject

    @model_validator(mode="after")
    def require_subject(self):
        # Ensures subject provided
```

### GenerateRequest

```python
class GenerateRequest(_SubjectRequestMixin, BaseModel):
    subject: Optional[Subject] = None
    brand: Optional[Subject] = None      # Excluded from serialization
    campaign: Campaign = Campaign()
    context: Optional[DialogContext] = None
    num_turns: int = 4                   # 1-20
    model: Optional[str] = None
    temperature: Optional[float] = None  # 0-2
    language: str = "ru"
```

### SingleResponseRequest

Same as `GenerateRequest` but `context` is required.

### CompareRequest

```python
class CompareRequest(_SubjectRequestMixin, BaseModel):
    subject: Optional[Subject] = None
    brand: Optional[Subject] = None
    campaign: Campaign = Campaign()
    context: Optional[DialogContext] = None
    models: list[str]                    # Required
    num_turns: int = 4
    language: str = "ru"
```

## Response Models

### ModelInfo

```python
class ModelInfo(BaseModel):
    name: str
    size: Optional[str] = None
    modified_at: Optional[str] = None
    digest: Optional[str] = None
```

### CompareResult

```python
class CompareResult(BaseModel):
    model: str
    dialog: GeneratedDialog
    generation_time_ms: int
```

## Type Constants

```python
SubjectType = Literal["brand", "product", "service", "topic", "info", "event"]
MentionStyle = Literal["natural", "casual", "enthusiastic", "skeptical"]
VALID_SUBJECT_TYPES = {"brand", "product", "service", "topic", "info", "event"}
VALID_MENTION_STYLES = {"natural", "casual", "enthusiastic", "skeptical"}
```

## Localization Data

```python
SUBJECT_TYPE_LABELS = {
    "ru": {"brand": "БРЕНД", "topic": "ТЕМА", ...},
    "en": {"brand": "BRAND", "topic": "TOPIC", ...}
}

MENTION_INSTRUCTIONS = {
    "ru": {"brand": "Упомяни {name} мимоходом...", ...},
    "en": {"brand": "Mention {name} casually...", ...}
}
```

## Validation Rules

| Model | Field | Constraint |
|-------|-------|------------|
| GenerateRequest | num_turns | 1-20 |
| GenerateRequest | temperature | 0-2 |
| GenerateRequest | subject/brand | At least one required |
| SingleResponseRequest | context | Required |
| CompareRequest | models | Required, non-empty |

## Related

- [Subject Types Feature](../requirements/feature-subject-types.md)
- [ADR-001: Subject over Brand](../decisions/ADR-001-subject-over-brand.md)
- [ADR-002: Brand as Factory](../decisions/ADR-002-brand-factory-function.md)
