# REST API Architecture

## Overview

FastAPI-based REST API for programmatic dialog generation. Located in `src/dialog_gen/api.py`.

## Server Configuration

| Setting | Default | Env Var |
|---------|---------|---------|
| Host | 0.0.0.0 | DIALOG_GEN_API_HOST |
| Port | 8100 | DIALOG_GEN_API_PORT |

**Start**: `dialog-gen serve` or `uvicorn dialog_gen.api:app`

## Application Setup

```python
app = FastAPI(
    title="Dialog Generator API",
    version="0.1.0"
)

# CORS enabled for all origins
app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)

# Lifecycle management
@asynccontextmanager
async def lifespan(app):
    yield
    await ollama.close()
```

## Endpoints

### GET /health

Health check endpoint.

**Response** (200):
```json
{"status": "ok"}
```

---

### GET /models

List available Ollama models.

**Response** (200):
```json
[
  {
    "name": "hermes3:8b",
    "size": "4.5 GB",
    "modified_at": "2024-01-15T10:30:00Z",
    "digest": "abc123..."
  }
]
```

**Errors**:
- 503: Ollama unavailable

---

### POST /generate

Generate complete dialog.

**Request**:
```json
{
  "subject": {
    "name": "Bitcoin ETF",
    "description": "investment news",
    "type": "topic",
    "attributes": ["SEC approved"]
  },
  "campaign": {
    "goal": "awareness",
    "style": "casual"
  },
  "context": {
    "messages": [
      {"role": "person1", "content": "hey"}
    ]
  },
  "num_turns": 4,
  "model": "hermes3:8b",
  "temperature": 0.8,
  "language": "en"
}
```

**Response** (200):
```json
{
  "messages": [
    {
      "role": "person1",
      "content": "have you heard about the bitcoin etf?",
      "delay_hint": 2.5
    },
    {
      "role": "person2",
      "content": "yeah its huge news!",
      "delay_hint": 1.8
    }
  ],
  "model_used": "hermes3:8b",
  "generation_params": {
    "provider": "ollama",
    "temperature": 0.8,
    "generation_time_ms": 1500,
    "raw_response_length": 320
  }
}
```

**Errors**:
- 400: Invalid request / Model not found
- 500: Generation failed

---

### POST /respond

Generate single response in context.

**Request**:
```json
{
  "subject": {...},
  "campaign": {...},
  "context": {
    "messages": [...]  // Required
  },
  "model": "hermes3:8b",
  "language": "ru"
}
```

**Response** (200):
```json
{
  "role": "person2",
  "content": "response text",
  "delay_hint": 2.1
}
```

---

### POST /compare

Compare multiple models.

**Request**:
```json
{
  "subject": {...},
  "models": ["hermes3:8b", "dolphin3:latest"],
  "num_turns": 4,
  "language": "ru"
}
```

**Response** (200):
```json
[
  {
    "model": "hermes3:8b",
    "dialog": {
      "messages": [...],
      "model_used": "hermes3:8b",
      "generation_params": {...}
    },
    "generation_time_ms": 1500
  },
  {
    "model": "dolphin3:latest",
    "dialog": {...},
    "generation_time_ms": 1800
  }
]
```

## Request Validation

- Pydantic models validate all inputs
- `subject` or `brand` required (not both needed)
- `num_turns`: 1-20
- `temperature`: 0-2
- `language`: ru/en

## Error Response Format

```json
{
  "detail": "Error message describing the issue"
}
```

## API Documentation

Auto-generated Swagger UI at `/docs` when server running.

## Usage Examples

### cURL

```bash
# Generate dialog
curl -X POST http://localhost:8100/generate \
  -H "Content-Type: application/json" \
  -d '{
    "subject": {
      "name": "FoodBox",
      "description": "food delivery",
      "type": "brand"
    },
    "num_turns": 4
  }'
```

### Python

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8100/generate",
        json={
            "subject": {
                "name": "FoodBox",
                "description": "food delivery"
            },
            "num_turns": 4
        }
    )
    dialog = response.json()
```

## Related

- [Dialog Generation Feature](../requirements/feature-dialog-generation.md)
- [Data Model](./data-model.md)
