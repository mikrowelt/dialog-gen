# CLAUDE.md — dialog-gen

## Workflow

**REQUIREMENTS → TESTS → IMPLEMENT → VERIFY → E2E → CHANGELOG → DOCS**

1. Update `docs/requirements/` before code changes
2. Write failing tests FIRST (TDD)
3. Implement minimal code to pass tests
4. Run `pytest -x --tb=short`
5. Deploy and verify — task NOT done until E2E passes
6. Update `CHANGELOG.md`
7. Update docs with class/function names for ast-grep

## Overview

AI dialog generation service. Generates conversation scripts for campaigns.

## Testing

```bash
pytest -x --tb=short      # Smoke test
pytest -v                 # Verbose
```
