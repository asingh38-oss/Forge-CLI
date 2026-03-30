"""
ui/renderer.py — Rich terminal rendering for Forge.
All visual output goes through here so the CLI looks consistent.
"""

import json
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.prompt import Confirm
from rich import box


FORGE_BANNER = r"""
 ___  ___  ____   ___  ____
| __]/ o _]|    \ / _] | ===]
| _] | [__]| || |/ [__ | [__
|_|  \____/|_||_|\____]|____]

  Autonomous CLI Coding Assistant
"""


def render_banner(console: Console):
    """Show the Forge startup banner."""
    console.print(
        Panel(
            FORGE_BANNER,
            style="bold bright_cyan",
            border_style="cyan",
            expand=False,
        )
    )


def render_tool_call(console: Console, tool_name: str, args: dict):
    """Display a tool call being made by the agent."""
    # Format args as a small table
    table = Table(
        show_header=False,
        box=box.SIMPLE,
        padding=(0, 1),
        style="dim",
    )
    table.add_column("key", style="bright_yellow")
    table.add_column("value", style="white")

    for k, v in args.items():
        val = str(v)
        if len(val) > 120:
            val = val[:120] + "..."
        table.add_row(k, val)

    console.print(
        Panel(
            table,
            title=f"[bold bright_yellow]⚙  Tool: {tool_name}[/]",
            border_style="yellow",
            expand=False,
        )
    )


def render_tool_result(console: Console, tool_name: str, result: str):
    """Display the result of a tool execution."""
    # Try to syntax highlight if it looks like code
    display = result[:2000] + ("..." if len(result) > 2000 else "")

    console.print(
        Panel(
            display,
            title=f"[bold green]✓  Result: {tool_name}[/]",
            border_style="green",
            expand=False,
            style="dim",
        )
    )


def render_assistant_message(console: Console, message: str):
    """Display the final assistant response."""
    console.print(
        Panel(
            message,
            title="[bold bright_cyan]◆  Forge[/]",
            border_style="bright_cyan",
            expand=True,
        )
    )


def render_error(console: Console, title: str, message: str):
    """Display an error message."""
    console.print(
        Panel(
            message,
            title=f"[bold red]✕  {title}[/]",
            border_style="red",
            expand=False,
        )
    )


def render_info(console: Console, message: str):
    """Display an informational message."""
    console.print(f"[dim cyan]ℹ  {message}[/]")


def render_model_switch(console: Console, provider: str, model: str):
    """Display a model switch confirmation."""
    console.print(
        f"[bold cyan]◆  Switched to [bright_yellow]{provider}[/] "
        f"([white]{model}[/])[/]"
    )


def confirm_tool_execution(console: Console, tool_name: str) -> bool:
    """Ask the user to confirm before executing a destructive tool."""
    return Confirm.ask(
        f"  [yellow]Execute [bold]{tool_name}[/bold]?[/yellow]",
        console=console,
        default=True,
    )