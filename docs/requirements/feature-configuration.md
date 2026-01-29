# Feature: Configuration System

## Overview

Hierarchical configuration system supporting file-based config, environment variables, and runtime overrides.

## Configuration Priority (High to Low)

1. **Request parameters** - Per-request overrides
2. **CLI flags** - Command-line arguments
3. **Environment variables** - `DIALOG_GEN_*` prefix
4. **Config file** - `~/.config/dialog-gen/config.json`
5. **Default values** - Hardcoded defaults

## Configuration Sections

### models
| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `default` | string | "hermes3:8b" | Default model (legacy, use cloud models) |
| `fallback` | string | "dolphin3:latest" | Fallback model (legacy) |
| `comparison` | string[] | [...] | Models for comparison |

### generation
| Setting | Type | Default | Range | Description |
|---------|------|---------|-------|-------------|
| `temperature` | float | 0.8 | 0-2 | Creativity level |
| `top_p` | float | 0.9 | 0-1 | Nucleus sampling |
| `max_tokens` | int | 2048 | - | Max output tokens |
| `default_turns` | int | 4 | 1-20 | Default message count |

### style
| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `language` | string | "ru" | Default language |
| `max_message_length` | int | 100 | Soft char limit |
| `match_context_style` | bool | true | Match input style |
| `show_delays` | bool | true | Show typing delays |

### cloud
| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `provider` | string | "anthropic" | Default provider |
| `openai_api_key` | string | null | OpenAI API key |
| `anthropic_api_key` | string | null | Anthropic API key |
| `openai_base_url` | string | "https://api.openai.com/v1" | OpenAI endpoint |
| `anthropic_base_url` | string | "https://api.anthropic.com" | Anthropic endpoint |
| `openai_model` | string | "gpt-4o-mini" | Default OpenAI model |
| `anthropic_model` | string | "claude-3-haiku-20240307" | Default Anthropic model |

### api
| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `host` | string | "0.0.0.0" | API bind host |
| `port` | int | 8100 | API port |

### prompts
Language-specific prompt templates (see [Multi-Language](./feature-multi-language.md)).

## Environment Variables

| Variable | Maps To |
|----------|---------|
| `DIALOG_GEN_MODEL` | models.default |
| `DIALOG_GEN_TEMPERATURE` | generation.temperature |
| `DIALOG_GEN_MAX_TOKENS` | generation.max_tokens |
| `DIALOG_GEN_LANGUAGE` | style.language |
| `DIALOG_GEN_API_HOST` | api.host |
| `DIALOG_GEN_API_PORT` | api.port |
| `DIALOG_GEN_PROVIDER` | cloud.provider |
| `DIALOG_GEN_OPENAI_API_KEY` | cloud.openai_api_key |
| `DIALOG_GEN_ANTHROPIC_API_KEY` | cloud.anthropic_api_key |
| `DIALOG_GEN_OPENAI_MODEL` | cloud.openai_model |
| `DIALOG_GEN_ANTHROPIC_MODEL` | cloud.anthropic_model |

## CLI Commands

```bash
# View
dialog-gen config show              # All settings
dialog-gen config show models       # Single section
dialog-gen config get models.default

# Modify
dialog-gen config set cloud.provider anthropic
dialog-gen config set generation.temperature 0.9

# Export/Import
dialog-gen config export config.json
dialog-gen config import config.json --merge

# Reset
dialog-gen config reset             # All
dialog-gen config reset models      # Single section
```

## Code Reference (ast-grep)

### Classes
- `class Settings` - Root configuration model
- `class ModelsConfig` - Model settings section
- `class GenerationConfig` - Generation parameters section
- `class StyleConfig` - Style settings section
- `class CloudConfig` - Cloud provider settings section
- `class ApiConfig` - API server settings section
- `class PromptsConfig` - Prompt templates section
- `class BrandDefaults` - Default brand/subject settings

### Key Functions
- `def load_config() -> Settings` - Load config from file + env
- `def save_config(cfg: Settings) -> None` - Save config to file
- `def get_config_path() -> Path` - Get config file path
- `def get_prompt(self, language: str, key: str) -> str` - Get localized prompt template

### Global Instance
- `settings` - Global Settings singleton

### CLI Commands
- `config_show()` - Show configuration
- `config_set()` - Set a value
- `config_get()` - Get a value
- `config_reset()` - Reset to defaults
- `config_edit()` - Open in editor
- `config_export()` - Export to file
- `config_import()` - Import from file

## Verification Criteria

- [x] Config file loads on startup
- [x] Environment variables override file
- [x] CLI flags override both
- [x] Request params override all
- [x] API keys masked in `config show`
- [x] Invalid values rejected

## Related

- [CLI Architecture](../architecture/cli.md)
