"""
CLI for dialog generation and model testing.

Provides commands for generating dialogs, comparing models,
and managing configuration.
"""

import asyncio
import json
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.tree import Tree
from typing import Optional
from pathlib import Path

from .cloud_client import get_cloud_client, reset_cloud_client
from .generator import DialogGenerator
from .models import Subject, Brand, Campaign, DialogContext, GenerateRequest
from .settings import settings, load_config, save_config, get_config_path, Settings

app = typer.Typer(help="Dialog Generator - Generate natural dialogs with brand mentions")
config_app = typer.Typer(help="Manage configuration settings")
app.add_typer(config_app, name="config")

console = Console()


# ============================================================================
# MODEL COMMANDS
# ============================================================================

@app.command()
def models():
    """List available models."""
    async def _list():
        cloud = get_cloud_client()
        return await cloud.list_models()

    result = asyncio.run(_list())

    table = Table(title="Available OpenRouter Models")
    table.add_column("Name", style="cyan")

    for name in result:
        table.add_row(name)

    console.print(table)


@app.command()
def recommend():
    """Show recommended models for dialog generation."""
    console.print("\n[bold cyan]OpenRouter Models[/bold cyan]")
    cloud_models = [
        ("anthropic/claude-3-haiku-20240307", "Fast & cheap, good for dialog"),
        ("anthropic/claude-3-5-haiku-20241022", "Newer Haiku, better quality"),
        ("anthropic/claude-sonnet-4-20250514", "Best quality, higher cost"),
        ("meta-llama/llama-3.3-70b-instruct", "Open source, good quality"),
    ]

    table = Table()
    table.add_column("Model", style="cyan")
    table.add_column("Description", style="green")

    for model, desc in cloud_models:
        table.add_row(model, desc)

    console.print(table)

    console.print("\n[dim]Set API key: dialog-gen config set cloud.openrouter_api_key sk-or-...[/dim]")
    console.print("[dim]Set model: dialog-gen config set cloud.openrouter_model anthropic/claude-3-haiku-20240307[/dim]")


# ============================================================================
# GENERATION COMMANDS
# ============================================================================

def _get_role_color(role: str) -> str:
    """Get color for role display."""
    colors = ["green", "yellow", "cyan", "magenta"]
    if role.startswith("person"):
        try:
            num = int(role.replace("person", ""))
            return colors[(num - 1) % len(colors)]
        except ValueError:
            pass
    return "white"


@app.command()
def generate(
    # New Subject-based options
    name: str = typer.Option(None, "--name", "-n", help="Subject name (e.g., 'FoodBox', 'Bitcoin ETF')"),
    description: str = typer.Option(None, "--desc", "-d", help="What it is (e.g., 'food delivery', 'investment news')"),
    subject_type: str = typer.Option("brand", "--type", "-t", help="Type: brand, product, service, topic, info, event"),
    attributes: str = typer.Option("", "--attr", "-a", help="Comma-separated attributes/features"),
    constraints: str = typer.Option("", "--constraints", help="Comma-separated things NOT to mention"),
    # Backward compatibility aliases
    brand_name: str = typer.Option(None, "--brand", "-b", help="[Alias for --name] Brand name"),
    what_is_it: str = typer.Option(None, "--what", "-w", help="[Alias for --desc] What the brand is"),
    features: str = typer.Option(None, "--features", "-f", help="[Alias for --attr] Comma-separated features"),
    # Common options
    context_file: str = typer.Option(None, "--context", "-c", help="JSON file with context"),
    model: str = typer.Option(None, "--model", "-m", help="Model to use"),
    provider: str = typer.Option(None, "--provider", "-p", help="Provider (openrouter)"),
    turns: int = typer.Option(None, "--turns", help="Number of messages"),
    language: str = typer.Option(None, "--lang", "-l", help="Language: ru, en"),
    temperature: float = typer.Option(None, "--temp", help="Temperature (0-2)")
):
    """Generate a dialog with natural subject mentions.

    Supports flexible subject types: brands, topics, information, events, etc.

    Examples:
        # Brand/product (marketing) - old syntax still works
        dialog-gen generate -b "FoodBox" -w "food delivery" -f "fast,cheap"

        # Brand/product (marketing) - new syntax
        dialog-gen generate -n "FoodBox" -d "food delivery" -t brand -a "fast,cheap"

        # Topic injection (news, trends)
        dialog-gen generate -n "Bitcoin ETF" -d "investment news" -t topic

        # Information seeding
        dialog-gen generate -n "Python 3.13" -d "new features" -t info -a "GIL removal,JIT"

        # With cloud model
        dialog-gen generate -n "FoodBox" -d "food delivery" -p anthropic -m haiku
    """
    # Handle backward compatibility: --brand/--what -> --name/--desc
    actual_name = name or brand_name
    actual_description = description or what_is_it
    actual_attributes = attributes or features or ""

    # Validate required fields
    if not actual_name:
        console.print("[red]Error: --name (-n) or --brand (-b) is required[/red]")
        raise typer.Exit(1)
    if not actual_description:
        console.print("[red]Error: --desc (-d) or --what (-w) is required[/red]")
        raise typer.Exit(1)

    # Use settings defaults
    turns = turns or settings.generation.default_turns
    language = language or settings.style.language
    temperature = temperature or settings.generation.temperature

    # Always use OpenRouter
    provider = "openrouter"

    # Set default model
    if not model:
        model = settings.cloud.openrouter_model

    async def _generate():
        # Create Subject (works for both old Brand and new flexible types)
        subject = Subject(
            name=actual_name,
            description=actual_description,
            type=subject_type,
            attributes=[a.strip() for a in actual_attributes.split(",") if a.strip()],
            constraints=[c.strip() for c in constraints.split(",") if c.strip()]
        )

        # Load context if provided
        context = None
        if context_file:
            ctx_path = Path(context_file)
            if ctx_path.exists():
                with open(ctx_path) as f:
                    messages = json.load(f)
                context = DialogContext(messages=messages)
                console.print(f"[dim]Loaded {len(messages)} context messages[/dim]")
            else:
                console.print(f"[red]Context file not found: {context_file}[/red]")
                return None

        request = GenerateRequest(
            subject=subject,
            context=context,
            num_turns=turns,
            model=model,
            language=language,
            temperature=temperature
        )

        generator = DialogGenerator(model=request.model, provider=provider)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            type_label = subject.get_type_label("en")
            task = progress.add_task(f"Generating {type_label.lower()} dialog with {request.model} ({provider})...", total=None)
            result = await generator.generate_dialog(request)
            progress.update(task, description="[green]Done!")

        return result

    result = asyncio.run(_generate())

    if result is None:
        return

    # Show context if provided
    if context_file:
        console.print("\n[bold dim]Context (input):[/bold dim]")
        with open(Path(context_file)) as f:
            ctx_msgs = json.load(f)
        for msg in ctx_msgs[-8:]:
            role = msg.get("role", "person1")
            color = _get_role_color(role)
            content = msg.get("content", msg.get("text", ""))[:60]
            console.print(f"  [{color}]{role}:[/{color}] {content}")
        if len(ctx_msgs) > 8:
            console.print(f"  [dim]... ({len(ctx_msgs) - 8} more)[/dim]")
        console.print()

    # Show result
    provider_used = result.generation_params.get('provider', 'openrouter')
    console.print(Panel(
        f"[bold]Provider:[/bold] {provider_used}\n"
        f"[bold]Model:[/bold] {result.model_used}\n"
        f"[bold]Time:[/bold] {result.generation_params.get('generation_time_ms', 0)}ms\n"
        f"[bold]Messages:[/bold] {len(result.messages)}\n"
        f"[bold]Subject:[/bold] {actual_name} ({subject_type})",
        title="Generation Info"
    ))

    console.print("\n[bold cyan]Generated Dialog:[/bold cyan]\n")
    for msg in result.messages:
        color = _get_role_color(msg.role)
        console.print(f"[{color}]{msg.role.upper()}:[/{color}] {msg.content}")
        if settings.style.show_delays and msg.delay_hint:
            console.print(f"  [dim](~{msg.delay_hint}s delay)[/dim]")
        console.print()


@app.command()
def compare(
    # New Subject-based options
    name: str = typer.Option(None, "--name", "-n", help="Subject name"),
    description: str = typer.Option(None, "--desc", "-d", help="What it is"),
    subject_type: str = typer.Option("brand", "--type", "-t", help="Type: brand, topic, info, etc."),
    # Backward compat
    brand_name: str = typer.Option(None, "--brand", "-b", help="[Alias for --name] Brand name"),
    what_is_it: str = typer.Option(None, "--what", "-w", help="[Alias for --desc] What the brand is"),
    # Common options
    models_list: str = typer.Option(None, "--models", "-m", help="Comma-separated models"),
    turns: int = typer.Option(None, "--turns", help="Number of messages"),
    language: str = typer.Option(None, "--lang", "-l", help="Language: ru, en")
):
    """Compare dialog generation across multiple models."""
    # Handle backward compatibility
    actual_name = name or brand_name
    actual_description = description or what_is_it

    if not actual_name:
        console.print("[red]Error: --name (-n) or --brand (-b) is required[/red]")
        raise typer.Exit(1)
    if not actual_description:
        console.print("[red]Error: --desc (-d) or --what (-w) is required[/red]")
        raise typer.Exit(1)

    # Use settings defaults
    if models_list:
        model_names = [m.strip() for m in models_list.split(",")]
    else:
        model_names = settings.models.comparison

    turns = turns or settings.generation.default_turns
    language = language or settings.style.language

    async def _compare():
        subject = Subject(name=actual_name, description=actual_description, type=subject_type)
        results = []

        for model_name in model_names:
            console.print(f"\n[cyan]Testing {model_name}...[/cyan]")

            request = GenerateRequest(
                subject=subject,
                num_turns=turns,
                model=model_name,
                language=language
            )

            generator = DialogGenerator(model=model_name)

            try:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task("Generating...", total=None)
                    result = await generator.generate_dialog(request)
                    progress.update(task, description="[green]Done!")

                results.append((model_name, result))
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")

        return results

    results = asyncio.run(_compare())

    console.print("\n" + "=" * 60)
    console.print("[bold]COMPARISON RESULTS[/bold]")
    console.print("=" * 60 + "\n")

    for model_name, result in results:
        console.print(Panel(
            f"[bold]Time:[/bold] {result.generation_params.get('generation_time_ms', 0)}ms",
            title=f"[cyan]{model_name}[/cyan]"
        ))

        for msg in result.messages:
            color = _get_role_color(msg.role)
            console.print(f"  [{color}]{msg.role.upper()}:[/{color}] {msg.content}")

        console.print()


@app.command()
def interactive(
    # New Subject-based options
    name: str = typer.Option(None, "--name", "-n", help="Subject name"),
    description: str = typer.Option(None, "--desc", "-d", help="What it is"),
    subject_type: str = typer.Option("brand", "--type", "-t", help="Type: brand, topic, info, etc."),
    # Backward compat
    brand_name: str = typer.Option(None, "--brand", "-b", help="[Alias for --name] Brand name"),
    what_is_it: str = typer.Option(None, "--what", "-w", help="[Alias for --desc] What the brand is"),
    # Common
    model: str = typer.Option(None, "--model", "-m", help="Model to use")
):
    """Interactive dialog session."""
    from .models import SingleResponseRequest

    # Handle backward compatibility
    actual_name = name or brand_name
    actual_description = description or what_is_it

    if not actual_name:
        console.print("[red]Error: --name (-n) or --brand (-b) is required[/red]")
        raise typer.Exit(1)
    if not actual_description:
        console.print("[red]Error: --desc (-d) or --what (-w) is required[/red]")
        raise typer.Exit(1)

    async def _session():
        subject = Subject(name=actual_name, description=actual_description, type=subject_type)
        generator = DialogGenerator(model=model or settings.cloud.openrouter_model)
        messages = []

        console.print(f"\n[bold cyan]Interactive Dialog Session[/bold cyan]")
        console.print(f"Model: {model or settings.cloud.openrouter_model}")
        console.print(f"Subject: {actual_name} ({subject_type})")
        console.print("[dim]Type 'quit' to exit, 'clear' to reset[/dim]\n")

        while True:
            user_input = console.input("[green]You (person1):[/green] ")

            if user_input.lower() == "quit":
                break
            if user_input.lower() == "clear":
                messages = []
                console.print("[dim]Conversation cleared[/dim]")
                continue

            messages.append({"role": "person1", "content": user_input})

            context = DialogContext(messages=messages)
            request = SingleResponseRequest(
                subject=subject,
                campaign=Campaign(),
                context=context,
                model=model
            )

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Thinking...", total=None)
                response = await generator.generate_single_response(request)
                progress.update(task, description="")

            messages.append({"role": response.role, "content": response.content})
            color = _get_role_color(response.role)
            console.print(f"[{color}]{response.role.upper()}:[/{color}] {response.content}\n")

    asyncio.run(_session())


@app.command()
def serve(
    host: str = typer.Option(None, "--host", "-h"),
    port: int = typer.Option(None, "--port", "-p")
):
    """Start the API server."""
    import uvicorn

    host = host or settings.api.host
    port = port or settings.api.port

    console.print(f"[green]Starting server at http://{host}:{port}[/green]")
    console.print(f"[dim]API docs: http://{host}:{port}/docs[/dim]")
    uvicorn.run("dialog_gen.api:app", host=host, port=port, reload=True)


# ============================================================================
# CONFIG COMMANDS
# ============================================================================

@config_app.command("show")
def config_show(
    section: str = typer.Argument(None, help="Section: models, generation, style, prompts, cloud, api, brand_defaults")
):
    """Show current configuration."""
    cfg = load_config()

    if section:
        section_map = {
            "models": cfg.models,
            "generation": cfg.generation,
            "style": cfg.style,
            "prompts": cfg.prompts,
            "cloud": cfg.cloud,
            "api": cfg.api,
            "brand_defaults": cfg.brand_defaults,
        }
        if section not in section_map:
            console.print(f"[red]Unknown section: {section}[/red]")
            console.print(f"Available: {', '.join(section_map.keys())}")
            return

        data = section_map[section].model_dump()
        # Mask API keys
        if section == "cloud":
            for key in ["openrouter_api_key"]:
                if data.get(key):
                    data[key] = data[key][:8] + "..." if len(data[key]) > 8 else "***"
        console.print(Panel(
            Syntax(json.dumps(data, indent=2, ensure_ascii=False), "json", theme="monokai"),
            title=f"[cyan]{section}[/cyan]"
        ))
    else:
        tree = Tree("[bold]dialog-gen config[/bold]")

        for name, section_obj in [
            ("models", cfg.models),
            ("generation", cfg.generation),
            ("style", cfg.style),
            ("prompts", cfg.prompts),
            ("cloud", cfg.cloud),
            ("api", cfg.api),
            ("brand_defaults", cfg.brand_defaults),
        ]:
            branch = tree.add(f"[cyan]{name}[/cyan]")
            data = section_obj.model_dump()
            for key, value in data.items():
                # Mask API keys
                if "api_key" in key and value:
                    value = value[:8] + "..." if len(value) > 8 else "***"
                elif isinstance(value, str) and len(value) > 50:
                    value = value[:50] + "..."
                elif isinstance(value, dict):
                    value = "{...}"
                branch.add(f"[green]{key}[/green]: {value}")

        console.print(tree)
        console.print(f"\n[dim]Config: {get_config_path()}[/dim]")


@config_app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Key (e.g., models.default)"),
    value: str = typer.Argument(..., help="New value")
):
    """Set a configuration value.

    Examples:
        dialog-gen config set models.default dolphin3:latest
        dialog-gen config set generation.temperature 0.9
        dialog-gen config set cloud.provider openai
        dialog-gen config set cloud.openai_api_key sk-...
    """
    cfg = load_config()

    parts = key.split(".")
    if len(parts) != 2:
        console.print("[red]Key format: section.field (e.g., models.default)[/red]")
        return

    section, field = parts

    section_map = {
        "models": cfg.models,
        "generation": cfg.generation,
        "style": cfg.style,
        "cloud": cfg.cloud,
        "api": cfg.api,
        "brand_defaults": cfg.brand_defaults,
    }

    if section == "prompts":
        console.print("[yellow]Use 'dialog-gen config edit' for prompts[/yellow]")
        return

    if section not in section_map:
        console.print(f"[red]Unknown section: {section}[/red]")
        return

    section_obj = section_map[section]
    if not hasattr(section_obj, field):
        console.print(f"[red]Unknown field: {field}[/red]")
        fields = list(section_obj.model_dump().keys())
        console.print(f"Available: {', '.join(fields)}")
        return

    current = getattr(section_obj, field)
    try:
        if isinstance(current, bool):
            new_value = value.lower() in ("true", "1", "yes")
        elif isinstance(current, int):
            new_value = int(value)
        elif isinstance(current, float):
            new_value = float(value)
        elif isinstance(current, list):
            new_value = json.loads(value)
        else:
            new_value = value

        setattr(section_obj, field, new_value)
        save_config(cfg)
        console.print(f"[green]Set {key} = {new_value}[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@config_app.command("get")
def config_get(key: str = typer.Argument(..., help="Key (e.g., models.default)")):
    """Get a configuration value."""
    cfg = load_config()

    parts = key.split(".")
    if len(parts) < 2:
        console.print("[red]Key format: section.field[/red]")
        return

    section = parts[0]
    field = ".".join(parts[1:])

    section_map = {
        "models": cfg.models,
        "generation": cfg.generation,
        "style": cfg.style,
        "prompts": cfg.prompts,
        "cloud": cfg.cloud,
        "api": cfg.api,
        "brand_defaults": cfg.brand_defaults,
    }

    if section not in section_map:
        console.print(f"[red]Unknown section: {section}[/red]")
        return

    section_obj = section_map[section]

    # Handle nested prompts (prompts.ru.system_prefix)
    if section == "prompts" and "." in field:
        lang, prompt_field = field.split(".", 1)
        if lang == "ru":
            value = getattr(cfg.prompts.ru, prompt_field, None)
        else:
            value = getattr(cfg.prompts.en, prompt_field, None)
    else:
        value = getattr(section_obj, field, None)

    if value is None:
        console.print(f"[red]Unknown field: {field}[/red]")
        return

    # Mask API keys
    if "api_key" in field and value:
        display_value = value[:8] + "..." if len(value) > 8 else "***"
    else:
        display_value = value

    console.print(f"[cyan]{key}[/cyan] = {display_value}")


@config_app.command("reset")
def config_reset(
    section: str = typer.Argument(None, help="Section to reset (or all)"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation")
):
    """Reset configuration to defaults."""
    if not force:
        msg = f"Reset {section} to defaults?" if section else "Reset ALL settings?"
        if not typer.confirm(msg):
            console.print("[yellow]Cancelled[/yellow]")
            return

    if section:
        cfg = load_config()
        defaults = Settings()

        section_map = {
            "models": ("models", defaults.models),
            "generation": ("generation", defaults.generation),
            "style": ("style", defaults.style),
            "prompts": ("prompts", defaults.prompts),
            "cloud": ("cloud", defaults.cloud),
            "api": ("api", defaults.api),
            "brand_defaults": ("brand_defaults", defaults.brand_defaults),
        }

        if section not in section_map:
            console.print(f"[red]Unknown section: {section}[/red]")
            return

        attr_name, default_obj = section_map[section]
        setattr(cfg, attr_name, default_obj)
        save_config(cfg)
        # Reset cloud client if cloud section was reset
        if section == "cloud":
            reset_cloud_client()
        console.print(f"[green]Reset {section}[/green]")
    else:
        save_config(Settings())
        reset_cloud_client()
        console.print("[green]Reset all settings[/green]")


@config_app.command("edit")
def config_edit():
    """Open config file in editor."""
    import subprocess
    import os

    cfg_path = get_config_path()
    if not cfg_path.exists():
        save_config(load_config())

    editor = os.environ.get("EDITOR", "vim")
    try:
        subprocess.run([editor, str(cfg_path)])
        console.print(f"[green]Saved: {cfg_path}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print(f"[dim]File: {cfg_path}[/dim]")


@config_app.command("path")
def config_path():
    """Show config file path."""
    console.print(f"[cyan]{get_config_path()}[/cyan]")


@config_app.command("export")
def config_export(output: str = typer.Argument(None, help="Output file (default: stdout)")):
    """Export configuration to file."""
    cfg = load_config()
    data = json.dumps(cfg.model_dump(), indent=2, ensure_ascii=False)

    if output:
        Path(output).write_text(data, encoding="utf-8")
        console.print(f"[green]Exported to {output}[/green]")
    else:
        console.print(Syntax(data, "json", theme="monokai"))


@config_app.command("import")
def config_import(
    input_file: str = typer.Argument(..., help="Config file to import"),
    merge: bool = typer.Option(False, "--merge", "-m", help="Merge with existing")
):
    """Import configuration from file."""
    try:
        with open(input_file) as f:
            data = json.load(f)

        if merge:
            current = load_config().model_dump()
            for section, values in data.items():
                if section in current and isinstance(values, dict):
                    current[section].update(values)
                else:
                    current[section] = values
            data = current

        cfg = Settings(**data)
        save_config(cfg)
        console.print(f"[green]Imported from {input_file}[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    app()
