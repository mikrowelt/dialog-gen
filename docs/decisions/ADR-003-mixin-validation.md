# ADR-003: Mixin for Request Validation

## Status

Accepted

## Context

The API has multiple request models that need similar validation logic:

```python
class GenerateRequest(BaseModel):
    subject: Optional[Subject] = None
    brand: Optional[Subject] = None  # Legacy
    # Need: ensure at least one is provided

class SingleResponseRequest(BaseModel):
    subject: Optional[Subject] = None
    brand: Optional[Subject] = None  # Legacy
    # Same validation needed

class CompareRequest(BaseModel):
    subject: Optional[Subject] = None
    brand: Optional[Subject] = None  # Legacy
    # Same validation again
```

Duplicating validation logic across models leads to:
- Code duplication
- Inconsistent error messages
- Risk of divergence

## Decision

Create a mixin class `_SubjectRequestMixin` that provides:

1. Common fields (`subject`, `brand`)
2. Shared validator
3. Unified subject resolution

```python
class _SubjectRequestMixin(BaseModel):
    """Mixin providing subject/brand fields and validation."""
    subject: Optional[Subject] = None
    brand: Optional[Subject] = None  # Legacy compat

    @model_validator(mode="after")
    def validate_subject_or_brand(self):
        if not self.subject and not self.brand:
            raise ValueError("Either 'subject' or 'brand' required")
        return self

    def get_subject(self) -> Subject:
        """Get subject, preferring new field over legacy."""
        return self.subject or self.brand

class GenerateRequest(_SubjectRequestMixin):
    # Inherits subject/brand and validation
    num_turns: int = 4
    ...
```

## Consequences

### Positive

- **DRY**: Validation logic in one place
- **Consistency**: Same error messages across endpoints
- **Maintainability**: Single point of change
- **Extensibility**: New request models inherit behavior

### Negative

- **Indirection**: Must check mixin to understand validation
- **Diamond problem**: Care needed if mixing with other base classes

### Implementation Notes

The mixin uses `model_validator(mode="after")` which:
- Runs after field validation
- Has access to all field values
- Can raise ValueError for custom errors

## Related

- [ADR-002: Brand as Factory Function](./ADR-002-brand-factory-function.md)
- [API Architecture](../architecture/api.md)
