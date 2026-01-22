# CLAUDE.md — dialog-gen

> Inherits workflow from [../CLAUDE.md](../CLAUDE.md)

## Development Workflow (MANDATORY)

```
REQUIREMENTS → TESTS → IMPLEMENT → VERIFY → CHANGELOG
```

1. **Requirements First** — Update `docs/requirements/` before any code change
2. **TDD** — Write failing tests in `tests/` BEFORE implementation
3. **Implement** — Write minimal code to make tests pass
4. **Verify** — Run `pytest -x --tb=short`
5. **Changelog** — Update `CHANGELOG.md`

## First Steps

**Before making changes:** Read `docs/` and understand how this project integrates with tg-master.

## ast-grep Patterns

```python
# Generator classes
"class DialogGenerator"

# Generation functions
"async def generate($$$)"
"def generate_dialog($$$)"
```

## Testing

```bash
pytest -x --tb=short             # Smoke test
pytest -v                        # Verbose
```

| What | How | Location |
|------|-----|----------|
| Generators | Unit tests with mocked AI | `tests/` |
| Output parsing | Unit tests with sample responses | `tests/` |

Mock Anthropic API calls in tests.

## Changelog

**REQUIRED:** Update `CHANGELOG.md` with every change — features, fixes, refactors.

## Notes

- Main package: `src/dialog_gen/`
- Integrates with tg-master DialogService
