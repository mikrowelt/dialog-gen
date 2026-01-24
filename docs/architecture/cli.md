# CLI Architecture

## Overview

Typer-based command-line interface with Rich console output. Located in `src/dialog_gen/cli.py`.

## Command Structure

```
dialog-gen
├── generate          # Generate dialog
├── compare           # Compare models
├── interactive       # Interactive session
├── serve             # Start API server
├── models            # List models
├── pull              # Download model
├── recommend         # Show recommended models
└── config            # Configuration subcommands
    ├── show          # Display config
    ├── set           # Set value
    ├── get           # Get value
    ├── reset         # Reset to defaults
    ├── edit          # Open in editor
    ├── path          # Show config path
    ├── export        # Export config
    └── import        # Import config
```

## Generation Commands

### dialog-gen generate

Generate dialog with subject mention.

**Options**:
| Flag | Short | Description |
|------|-------|-------------|
| `--name` | `-n` | Subject name |
| `--desc` | `-d` | Description |
| `--type` | `-t` | Subject type (default: brand) |
| `--attr` | `-a` | Comma-separated attributes |
| `--constraints` | | Things NOT to mention |
| `--brand` | `-b` | Legacy: brand name |
| `--what` | `-w` | Legacy: description |
| `--features` | `-f` | Legacy: features |
| `--context` | `-c` | Context JSON file |
| `--model` | `-m` | Model override |
| `--provider` | `-p` | Provider override |
| `--turns` | | Message count |
| `--lang` | `-l` | Language (ru/en) |
| `--temp` | | Temperature |

**Output**: Rich panel with generation info + formatted dialog.

### dialog-gen compare

Compare multiple models.

**Options**: Same as generate, plus:
| Flag | Short | Description |
|------|-------|-------------|
| `--models` | `-m` | Comma-separated models |

**Output**: Side-by-side results with timing.

### dialog-gen interactive

Interactive REPL session.

**Commands**:
- Type message → Get AI response
- `quit` → Exit
- `clear` → Reset conversation

## Model Commands

### dialog-gen models

List available models.

| Flag | Short | Description |
|------|-------|-------------|
| `--provider` | `-p` | Filter by provider |

**Output**: Rich table with name, size, modified date.

### dialog-gen pull \<model\>

Download Ollama model with progress bar.

### dialog-gen recommend

Show recommended models with descriptions.

## Configuration Commands

### dialog-gen config show [section]

Display configuration as tree (all) or panel (section).

### dialog-gen config set \<key\> \<value\>

Set config value. Key format: `section.field`

Type conversion:
- `true`/`false` → bool
- Numeric → int/float
- JSON array → list

### dialog-gen config get \<key\>

Get single value. Supports nested keys.

### dialog-gen config reset [section]

Reset to defaults. Requires `--force` or confirmation.

### dialog-gen config edit

Open config file in `$EDITOR` (default: vim).

### dialog-gen config export [file]

Export to JSON file or stdout.

### dialog-gen config import \<file\>

Import from JSON. `--merge` to merge vs replace.

## Server Command

### dialog-gen serve

Start FastAPI server.

| Flag | Short | Description |
|------|-------|-------------|
| `--host` | `-h` | Bind host (default: 0.0.0.0) |
| `--port` | `-p` | Port (default: 8100) |

## Output Formatting

### Rich Components Used

- `Console` - Main output
- `Panel` - Info boxes
- `Table` - Structured data
- `Tree` - Nested config
- `Progress` - Spinners and progress bars
- `Syntax` - JSON highlighting

### Role Colors

| Role | Color |
|------|-------|
| person1 | green |
| person2 | yellow |
| person3 | cyan |
| person4 | magenta |

## Error Handling

- Missing required args → Clear error message
- File not found → Red error text
- API errors → Exception details

## Async Execution

Generation commands use `asyncio.run()` wrapper:

```python
def generate(...):
    async def _generate():
        # Async implementation
    result = asyncio.run(_generate())
```

## Related

- [Configuration Feature](../requirements/feature-configuration.md)
- [Dialog Generation Feature](../requirements/feature-dialog-generation.md)
