# CLAUDE.md — dialog-gen

> Inherits workflow from [../CLAUDE.md](../CLAUDE.md)

---

## For Agents: Read This First

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  YOU ARE AN AGENT WORKING ON dialog-gen                                     │
│                                                                             │
│  MANDATORY WORKFLOW:                                                        │
│  1. Read this CLAUDE.md completely                                          │
│  2. Read docs/requirements/ for existing specs                              │
│  3. UPDATE docs/requirements/ with YOUR implementation specs                │
│  4. Write tests FIRST (TDD)                                                 │
│  5. Implement minimal code to pass tests                                    │
│  6. Run: pytest -x --tb=short                                               │
│  7. UPDATE docs/ with classes/functions you created                         │
│  8. UPDATE CHANGELOG.md                                                     │
│                                                                             │
│  LOCAL DOCS LOCATIONS:                                                      │
│  - Requirements: docs/requirements/*.md                                     │
│  - Changelog: CHANGELOG.md                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Development Workflow (MANDATORY)

```
REQUIREMENTS → TESTS → IMPLEMENT → VERIFY → E2E → CHANGELOG → DOCS
```

1. **Requirements First** — Update `docs/requirements/` before any code change
2. **TDD** — Write failing tests BEFORE implementation
3. **Implement** — Write minimal code to make tests pass
4. **Verify** — Run `pytest -x --tb=short`
5. **E2E** — Deploy and verify feature works
6. **Changelog** — Update `CHANGELOG.md`
7. **Update Docs** — Add class/function names to docs for ast-grep

## Testing

```bash
pytest -x --tb=short      # Smoke test
pytest -v                 # Verbose
```

## Changelog

**REQUIRED:** Update `CHANGELOG.md` with every change — features, fixes, refactors.

## Notes

- AI dialog generation service
- Generates conversation scripts for campaigns
