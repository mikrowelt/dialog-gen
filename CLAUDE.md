# CLAUDE.md — dialog-gen

> Inherits workflow from [../CLAUDE.md](../CLAUDE.md)

## Development Workflow (MANDATORY)

```
REQUIREMENTS → TESTS → IMPLEMENT → VERIFY → E2E → CHANGELOG → DOCS
```

1. **Requirements First** — Update `docs/requirements/` before any code change
2. **TDD** — Write failing tests in `tests/` BEFORE implementation
3. **Implement** — Write minimal code to make tests pass
4. **Verify** — Run `pytest -x --tb=short`
5. **E2E on Dev** — Deploy to dev, verify feature works. **Task NOT done until E2E passes**
6. **Changelog** — Update `CHANGELOG.md`
7. **Update Docs** — Add class/function/property names to docs for ast-grep

## First Steps: Read Docs → ast-grep → Code

1. **Read `docs/`** — Understand generator architecture, find class/function names
2. **Use ast-grep** — Search for those names in code (see patterns below)
3. **Analyze code** — Read with context from documentation

**Never search code blindly — read docs first to know what to search for.**

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
