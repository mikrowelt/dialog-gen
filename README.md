# dialog-gen

Local AI-powered dialog generator for natural subject mentions in Telegram-style conversations.

## Features

- Generate natural dialogs with subject mentions using local LLMs (via Ollama) or cloud (OpenAI, Anthropic)
- **Flexible subject types**: brands, products, topics, info, events
- Multi-person conversations (person1, person2, person3...)
- Context-aware generation - continue existing conversations
- Style matching - generated messages match input message style
- Multiple model support with comparison testing
- Comprehensive configuration system
- REST API server
- Multi-language support (Russian, English)

## Installation

```bash
cd dialog-gen
pip install -e .
```

## Quick Start

### Brand/Product Marketing (Original Use Case)

```bash
# Generate a dialog mentioning a brand
dialog-gen generate -b "FoodBox" -w "food delivery" -f "fast,cheap"

# Or use the new syntax
dialog-gen generate -n "FoodBox" -d "food delivery" -t brand -a "fast,cheap"
```

### Topic Injection (News, Trends)

```bash
# Inject a topic naturally into conversation
dialog-gen generate -n "Bitcoin ETF" -d "investment news" -t topic

# With attributes
dialog-gen generate -n "AI regulation" -d "tech policy" -t topic -a "EU Act,safety concerns"
```

### Information Seeding

```bash
# Seed specific information into dialog
dialog-gen generate -n "Python 3.13" -d "new features" -t info -a "GIL removal,JIT compiler"
```

### Event Mentions

```bash
# Naturally mention an event
dialog-gen generate -n "DevConf 2024" -d "tech conference" -t event -a "keynote,workshops"
```

## Subject Types

| Type | Use Case | Example |
|------|----------|---------|
| `brand` | Marketing, product placement | FoodBox, Nike, Apple |
| `product` | Specific product mentions | iPhone 16, Model Y |
| `service` | Service recommendations | Spotify, Netflix |
| `topic` | News, trends, discussions | Bitcoin ETF, Climate change |
| `info` | Facts, information seeding | Python 3.13 features |
| `event` | Events, conferences | DevConf 2024, World Cup |

## Commands

### Generation

```bash
dialog-gen generate [OPTIONS]

# New flexible options
  -n, --name TEXT       Subject name (e.g., 'FoodBox', 'Bitcoin ETF')
  -d, --desc TEXT       What it is (e.g., 'food delivery', 'investment news')
  -t, --type TEXT       Type: brand, product, service, topic, info, event (default: brand)
  -a, --attr TEXT       Comma-separated attributes/features
  --constraints TEXT    Comma-separated things NOT to mention

# Legacy options (still work)
  -b, --brand TEXT      [Alias for --name] Brand name
  -w, --what TEXT       [Alias for --desc] What the brand is
  -f, --features TEXT   [Alias for --attr] Comma-separated features

# Common options
  -c, --context PATH    JSON file with context messages
  -m, --model TEXT      Model to use
  -p, --provider TEXT   Provider: ollama, openai, anthropic
  --turns INT           Number of messages to generate (default: 4)
  -l, --lang TEXT       Language: ru, en (default: ru)
  --temp FLOAT          Temperature 0-2 (default: 0.8)
```

### Context File Format

```json
[
  {"role": "person1", "content": "hey, what's up?"},
  {"role": "person2", "content": "not much, working"},
  {"role": "person1", "content": "what are you working on?"}
]
```

### Model Management

```bash
dialog-gen models              # List available models
dialog-gen pull <model>        # Pull a model from Ollama
dialog-gen recommend           # Show recommended models
```

### Using Cloud Providers

```bash
# OpenAI
dialog-gen generate -n "FoodBox" -d "delivery" -p openai -m gpt-4o-mini

# Anthropic
dialog-gen generate -n "FoodBox" -d "delivery" -p anthropic -m haiku
```

### Comparison

```bash
dialog-gen compare -n "FoodBox" -d "delivery" -m "hermes3:8b,dolphin3:latest"
```

### Interactive Mode

```bash
dialog-gen interactive -n "FoodBox" -d "food delivery" -m hermes3:8b
```

### API Server

```bash
dialog-gen serve --host 0.0.0.0 --port 8100
```

API docs available at `http://localhost:8100/docs`

## Configuration

Configuration is stored in `~/.config/dialog-gen/config.json`

### View Configuration

```bash
dialog-gen config show              # Show all settings
dialog-gen config show models       # Show specific section
dialog-gen config get models.default
```

### Modify Configuration

```bash
dialog-gen config set models.default dolphin3:latest
dialog-gen config set generation.temperature 0.9
dialog-gen config set style.language en
dialog-gen config set cloud.anthropic_api_key sk-ant-...
```

### Cloud Provider Setup

```bash
# Set API keys
dialog-gen config set cloud.openai_api_key sk-...
dialog-gen config set cloud.anthropic_api_key sk-ant-...

# Or use environment variables
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
```

### Configuration Sections

#### models
| Setting | Default | Description |
|---------|---------|-------------|
| default | hermes3:8b | Default model for generation |
| fallback | dolphin3:latest | Fallback if default unavailable |
| comparison | [...] | Models for comparison tests |

#### generation
| Setting | Default | Description |
|---------|---------|-------------|
| temperature | 0.8 | Creativity (0-2) |
| top_p | 0.9 | Nucleus sampling |
| max_tokens | 2048 | Max output tokens |
| default_turns | 4 | Default message count |

#### style
| Setting | Default | Description |
|---------|---------|-------------|
| language | ru | Default language |
| max_message_length | 100 | Max chars per message |
| match_context_style | true | Match input style |
| show_delays | true | Show typing delays |

#### cloud
| Setting | Default | Description |
|---------|---------|-------------|
| provider | anthropic | Default cloud provider |
| openai_api_key | None | OpenAI API key |
| anthropic_api_key | None | Anthropic API key |
| openai_model | gpt-4o-mini | Default OpenAI model |
| anthropic_model | claude-3-haiku-... | Default Anthropic model |

## Recommended Models

### Local (Ollama)
| Model | Size | Description |
|-------|------|-------------|
| hermes3:8b | 8B | Best for roleplay, 100% brand mention |
| dolphin3:latest | 8B | Good reasoning, 100% brand mention |
| nous-hermes2:10.7b | 10.7B | Larger, faster but ~70% brand mention |

### Cloud
| Provider | Model | Best For |
|----------|-------|----------|
| Anthropic | claude-3-haiku | Fast, cheap, good quality |
| Anthropic | claude-3-sonnet | Higher quality |
| OpenAI | gpt-4o-mini | Fast, cheap |
| OpenAI | gpt-4o | Highest quality |

## API Endpoints

When running `dialog-gen serve`:

- `POST /generate` - Generate dialog
- `POST /respond` - Generate single response
- `POST /compare` - Compare models
- `GET /models` - List models
- `GET /health` - Health check

### API Request Example

```bash
curl -X POST http://localhost:8100/generate \
  -H "Content-Type: application/json" \
  -d '{
    "subject": {
      "name": "Bitcoin ETF",
      "description": "investment news",
      "type": "topic"
    },
    "num_turns": 4,
    "language": "en"
  }'
```

## Examples

### Generate with Real Context

```bash
# Create context file
cat > context.json << 'EOF'
[
  {"role": "person1", "content": "hey"},
  {"role": "person2", "content": "hey, what's up?"},
  {"role": "person1", "content": "bored, nothing to do"},
  {"role": "person2", "content": "same here"},
  {"role": "person1", "content": "hungry tbh"}
]
EOF

# Generate continuation with brand mention
dialog-gen generate -n "FoodBox" -d "food delivery" -c context.json
```

### Topic Discussion Generation

```bash
# Generate a discussion about a tech topic
dialog-gen generate \
  -n "Apple Vision Pro" \
  -d "mixed reality headset" \
  -t topic \
  -a "spatial computing,expensive,developer kit" \
  --lang en
```

### Information Seeding

```bash
# Seed specific facts into a conversation
dialog-gen generate \
  -n "Climate Summit 2024" \
  -d "global climate conference" \
  -t event \
  -a "net zero targets,renewable energy commitments" \
  --constraints "politics,controversy"
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=dialog_gen

# Type checking
mypy src/
```

## Programmatic Usage

```python
from dialog_gen.models import Subject, Campaign, GenerateRequest
from dialog_gen.generator import DialogGenerator

# Create a subject
subject = Subject(
    name="Bitcoin ETF",
    description="investment news",
    type="topic",
    attributes=["SEC approved", "institutional adoption"]
)

# Generate dialog
generator = DialogGenerator(model="hermes3:8b")
request = GenerateRequest(subject=subject, num_turns=4, language="en")
result = await generator.generate_dialog(request)

for msg in result.messages:
    print(f"{msg.role}: {msg.content}")
```

### Backward Compatibility

The old `Brand` interface still works:

```python
from dialog_gen.models import Brand, GenerateRequest

# Legacy style
brand = Brand(
    name="FoodBox",
    what_is_it="food delivery",
    features=["fast", "cheap"]
)

request = GenerateRequest(brand=brand, num_turns=4)
```

## License

MIT
