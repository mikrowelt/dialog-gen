# ADR-002: Brand as Factory Function

## Status

Accepted

## Context

After introducing the generic `Subject` model (ADR-001), we needed to maintain backward compatibility with existing code using the `Brand` class:

```python
# Existing code
brand = Brand(
    name="FoodBox",
    what_is_it="food delivery",
    features=["fast", "cheap"]
)
```

Options considered:

1. **Subclass**: `Brand(Subject)` with field mappings
   - Problem: Pydantic warnings about shadowing properties

2. **Type alias**: `Brand = Subject`
   - Problem: Loses field name compatibility

3. **Factory function**: `def Brand(...) -> Subject`
   - Maps legacy fields to new names
   - Returns `Subject` instance

## Decision

Implement `Brand` as a factory function that:
1. Accepts both legacy (`what_is_it`, `features`) and new (`description`, `attributes`) field names
2. Maps legacy fields to new equivalents
3. Returns a `Subject` instance with `type="brand"`

```python
def Brand(
    name: str,
    what_is_it: Optional[str] = None,
    description: Optional[str] = None,
    features: Optional[list[str]] = None,
    attributes: Optional[list[str]] = None,
    ...
) -> Subject:
    actual_description = description or what_is_it or ""
    actual_attributes = attributes or features or []
    ...
    return Subject(
        name=name,
        description=actual_description,
        type="brand",
        attributes=actual_attributes,
        ...
    )
```

## Consequences

### Positive

- **Full backward compatibility**: Existing code works unchanged
- **No Pydantic warnings**: No class inheritance issues
- **Flexible**: Accepts both old and new field names
- **Simple**: Easy to understand and maintain

### Negative

- **Not a class**: `isinstance(brand, Brand)` doesn't work
  - Use `isinstance(brand, Subject)` instead
- **Type hints**: IDE may not show Brand fields
  - Mitigated by docstring and type annotations

### Usage

```python
# Legacy style (still works)
brand = Brand(name="FoodBox", what_is_it="delivery", features=["fast"])

# New style (also works)
brand = Brand(name="FoodBox", description="delivery", attributes=["fast"])

# Result is always Subject
assert isinstance(brand, Subject)
assert brand.type == "brand"
```

## Related

- [ADR-001: Subject over Brand](./ADR-001-subject-over-brand.md)
- [Data Model](../architecture/data-model.md)
