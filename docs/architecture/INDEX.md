# Architecture Documentation

System design and component documentation for Dialog-Gen.

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interfaces                          │
├──────────────────────────┬──────────────────────────────────────┤
│      CLI (Typer)         │         REST API (FastAPI)          │
│   dialog-gen generate    │        POST /generate               │
│   dialog-gen compare     │        POST /respond                │
│   dialog-gen interactive │        POST /compare                │
└──────────────────────────┴──────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DialogGenerator                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐  │
│  │ Build Prompts   │→ │ Call LLM        │→ │ Parse Output   │  │
│  │ (system + user) │  │ (route to       │  │ (JSON/text)    │  │
│  │                 │  │  provider)      │  │                │  │
│  └─────────────────┘  └─────────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
            │   Ollama    │ │   OpenAI    │ │  Anthropic  │
            │  (Local)    │ │   (Cloud)   │ │  (Cloud)    │
            └─────────────┘ └─────────────┘ └─────────────┘
```

## Component Documentation

| Component | File | Description |
|-----------|------|-------------|
| [Data Model](./data-model.md) | `models.py` | Pydantic models and schemas |
| [Generator](./generator.md) | `generator.py` | Core dialog generation engine |
| [Providers](./providers.md) | `ollama_client.py`, `cloud_client.py` | LLM provider clients |
| [Utilities](./utils.md) | `utils.py` | Shared utility functions |
| [REST API](./api.md) | `api.py` | FastAPI endpoints |
| [CLI](./cli.md) | `cli.py` | Command-line interface |

## Data Flow

### Generation Request Flow

```
1. Request received (CLI/API)
   └── GenerateRequest with Subject, Campaign, Context

2. Generator processes request
   ├── _build_system_prompt()
   │   ├── Subject type label (localized)
   │   ├── Attributes/constraints
   │   └── Style rules + mention instructions
   │
   ├── _build_generation_prompt()
   │   ├── Context messages (if any)
   │   ├── Length constraints (for Russian)
   │   └── JSON output format
   │
   ├── _call_llm() [Provider dispatch]
   │   └── Ollama / OpenAI / Anthropic
   │
   ├── _parse_dialog()
   │   ├── JSON parsing (primary)
   │   └── Line-by-line (fallback)
   │
   └── _calculate_delay() [per message]

3. Return GeneratedDialog
   └── messages, model_used, generation_params
```

## Key Design Patterns

### Provider Abstraction
All LLM providers implement same generation interface, enabling seamless switching.

### Backward Compatibility
Legacy `Brand` API preserved via factory function and property aliases on `Subject`.

### Configuration Hierarchy
Layered config: defaults → file → environment → CLI → request.

### Mixin for Validation
`_SubjectRequestMixin` shares validation logic across request models.

## Module Dependencies

```
models.py           # No deps (data models only)
    ↑
settings.py         # Imports models
    ↑
utils.py            # No deps (shared utilities)
    ↑
ollama_client.py    # Imports settings
cloud_client.py     # Imports settings, utils
    ↑
generator.py        # Imports ollama, cloud_client, settings, models, utils
    ↑
api.py              # Imports generator, ollama, models, settings
cli.py              # Imports generator, ollama, cloud_client, models, settings, utils
```

## External Integrations

| Service | Protocol | Default URL |
|---------|----------|-------------|
| Ollama | HTTP/JSON | http://localhost:11434 |
| OpenAI | HTTP/JSON | https://api.openai.com/v1 |
| Anthropic | HTTP/JSON | https://api.anthropic.com |
