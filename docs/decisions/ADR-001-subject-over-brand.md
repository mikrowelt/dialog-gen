# ADR-001: Subject Model over Brand-specific Model

## Status

Accepted

## Context

The original system was designed specifically for brand marketing use cases, with a `Brand` model containing fields like `name`, `what_is_it`, `features`, `promo_code`, etc.

However, users needed to inject other types of content:
- **Topics**: News, trends, discussions (e.g., "Bitcoin ETF")
- **Information**: Facts to seed naturally (e.g., "Python 3.13 features")
- **Events**: Conferences, happenings (e.g., "DevConf 2024")

The brand-specific model was too restrictive for these use cases.

## Decision

Replace the brand-specific `Brand` model with a generic `Subject` model that supports multiple types:

```python
class Subject(BaseModel):
    name: str
    description: str
    type: str = "brand"  # brand, product, service, topic, info, event
    attributes: list[str] = []
    constraints: list[str] = []
    mention_style: str = "natural"
    context_hint: Optional[str] = None
    promo: Optional[dict] = None
```

Each subject type has:
- Localized type labels (БРЕНД, ТЕМА, etc.)
- Type-specific mention instructions
- Appropriate prompt generation

## Consequences

### Positive

- **Flexibility**: Same system handles marketing, news, education
- **Unified API**: Single model for all use cases
- **Extensibility**: New types can be added easily
- **Localization**: Type labels and instructions adapt to language

### Negative

- **Complexity**: More fields to understand
- **Migration**: Existing code using `Brand` needs updating
- **Documentation**: More use cases to document

### Mitigation

- Backward compatibility via `Brand()` factory function
- Property aliases on `Subject` for legacy field names
- Default `type="brand"` for marketing users

## Related

- [Subject Types Feature](../requirements/feature-subject-types.md)
- [Data Model](../architecture/data-model.md)
- [ADR-002: Brand as Factory](./ADR-002-brand-factory-function.md)
