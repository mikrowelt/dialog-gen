# Dialog-Gen Documentation

> AI-powered dialog generator for natural subject mentions in conversations

## Overview

Dialog-Gen generates realistic Telegram-style conversations with naturally embedded subject mentions. It supports multiple subject types (brands, topics, information, events), cloud LLM providers (OpenAI, Anthropic), and provides both CLI and REST API interfaces.

## Quick Links

| Section | Description |
|---------|-------------|
| [Requirements](./requirements/INDEX.md) | Feature specifications and user stories |
| [Architecture](./architecture/INDEX.md) | System design and component documentation |
| [Decisions](./decisions/INDEX.md) | Architecture Decision Records (ADRs) |

## Key Capabilities

- **6 Subject Types**: brand, product, service, topic, info, event
- **Multi-Language**: Russian and English with localized prompts
- **2 LLM Providers**: OpenAI, Anthropic
- **Context Awareness**: Continue existing conversations
- **Multi-Person**: Support for 3+ speakers
- **Dual Interface**: CLI and REST API

## Project Structure

```
dialog-gen/
├── src/dialog_gen/
│   ├── models.py          # Data models (Subject, Campaign, etc.)
│   ├── generator.py       # Core generation engine
│   ├── settings.py        # Configuration system
│   ├── utils.py           # Shared utilities (detect_provider)
│   ├── cloud_client.py    # OpenAI/Anthropic client
│   ├── api.py             # REST API (FastAPI)
│   └── cli.py             # CLI (Typer)
├── tests/                 # Test suite
└── docs/                  # This documentation
```

## Getting Started

```bash
# Install
pip install -e .

# Configure API key
dialog-gen config set cloud.anthropic_api_key sk-ant-...

# Generate dialog (brand)
dialog-gen generate -n "FoodBox" -d "food delivery" -t brand

# Generate dialog (topic)
dialog-gen generate -n "Bitcoin ETF" -d "investment news" -t topic

# Start API server
dialog-gen serve
```

## Configuration

Configuration stored at `~/.config/dialog-gen/config.json`

See [Configuration Feature](./requirements/feature-configuration.md) for details.

## API Reference

See [REST API](./architecture/api.md) for endpoint documentation.
