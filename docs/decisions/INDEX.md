# Architecture Decision Records

This section documents significant architecture and design decisions.

## ADR Log

| ID | Title | Status | Date |
|----|-------|--------|------|
| [ADR-001](./ADR-001-subject-over-brand.md) | Subject Model over Brand-specific Model | Accepted | 2024-01 |
| [ADR-002](./ADR-002-brand-factory-function.md) | Brand as Factory Function | Accepted | 2024-01 |
| [ADR-003](./ADR-003-mixin-validation.md) | Mixin for Request Validation | Accepted | 2024-01 |
| [ADR-004](./ADR-004-multi-language-prompts.md) | Language-specific Prompt Templates | Accepted | 2024-01 |

## ADR Template

```markdown
# ADR-XXX: Title

## Status
Proposed | Accepted | Deprecated | Superseded by ADR-XXX

## Context
What is the issue we're addressing?

## Decision
What have we decided to do?

## Consequences
What are the trade-offs?

### Positive
- ...

### Negative
- ...
```

## How to Add New ADRs

1. Create new file: `ADR-XXX-short-title.md`
2. Follow template above
3. Add entry to this INDEX
4. Link from relevant architecture/requirements docs
