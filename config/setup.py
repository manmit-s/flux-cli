import os
import re
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich import box
from rich.text import Text
from config.loader import get_config_dir, get_system_config_path

console = Console()


def run_config_wizard() -> bool:
    console.print()
    console.print(
        Panel(
            Text("Welcome to Flux-CLI First-Time Setup Wizard!\nThis wizard will configure your API key, Base URL, and Model ID.", style="bold #F6DBC0"),
            title="✦ Flux-CLI Setup",
            border_style="#502D55",
            box=box.ROUNDED,
            padding=(1, 2)
        )
    )

    # 1. API Key
    while True:
        api_key = Prompt.ask("[bold #c76f9d]Enter your API Key[/]").strip()
        if api_key:
            break
        console.print("[red]API Key cannot be empty.[/red]")

    # 2. Base URL
    default_base_url = "https://openrouter.ai/api/v1"
    while True:
        base_url = Prompt.ask(
            "[bold #8bcefc]Enter Base URL[/]",
            default=default_base_url
        ).strip()
        if base_url.startswith("http://") or base_url.startswith("https://"):
            break
        console.print("[red]Invalid Base URL. Must start with http:// or https://[/red]")

    # 3. Model ID
    default_model = "nvidia/nemotron-3-super-120b-a12b"
    model_id = Prompt.ask(
        "[bold #e7aafb]Enter Model ID[/]",
        default=default_model
    ).strip() or default_model

    # Build TOML content
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = get_system_config_path()

    toml_content = f"""# Flux-CLI System Configuration
api_key = "{api_key}"
base_url = "{base_url}"

[model]
name = "{model_id}"
temperature = 0.7
"""

    try:
        config_path.write_text(toml_content, encoding="utf-8")
        console.print(
            Panel(
                Text(f"Configuration successfully saved to:\n{config_path}", style="bold #4ade80"),
                title="✦ Setup Complete",
                border_style="#4ade80",
                box=box.ROUNDED,
                padding=(1, 2)
            )
        )
        return True
    except Exception as e:
        console.print(f"[bold red]Failed to save configuration: {e}[/bold red]")
        return False
