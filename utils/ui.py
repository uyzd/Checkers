import os
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich import box

console = Console()

RAINBOW = [
    "bold bright_cyan",
    "bold bright_magenta",
    "bold bright_blue",
    "bold cyan",
    "bold magenta",
    "bold bright_cyan",
]

ASCII_LINES = [
    r" ██╗  ██╗██████╗  ██████╗ ██╗  ██╗",
    r" ╚██╗██╔╝██╔══██╗██╔═══██╗╚██╗██╔╝",
    r"  ╚███╔╝ ██████╔╝██║   ██║ ╚███╔╝ ",
    r"  ██╔██╗ ██╔══██╗██║   ██║ ██╔██╗ ",
    r" ██╔╝ ██╗██████╔╝╚██████╔╝██╔╝ ██╗",
    r" ╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝",
]


def print_banner() -> None:
    console.clear()
    art = Text()
    for i, line in enumerate(ASCII_LINES):
        art.append(line + "\n", style=RAINBOW[i % len(RAINBOW)])
    console.print(art, justify="center")

    sub = Text()
    sub.append("Xbox Live Username Scanner", style="bold bright_green")
    sub.append("  ·  ", style="dim white")
    sub.append("Checks availability & posts to Discord", style="dim cyan")
    console.print(sub, justify="center")
    console.print()

    api_key = os.environ.get("XBL_API_KEY", "")
    webhook  = os.environ.get("DISCORD_WEBHOOK_URL", "")

    api_status = Text()
    if api_key:
        api_status.append("  ✓ ", style="bold bright_green")
        api_status.append("xbl.io API key loaded", style="bright_green")
    else:
        api_status.append("  ✗ ", style="bold red")
        api_status.append("xbl.io API key NOT set  ", style="red")
        api_status.append("(set XBL_API_KEY env var)", style="dim yellow")

    wh_status = Text()
    if webhook:
        wh_status.append("  ✓ ", style="bold bright_green")
        wh_status.append("Discord webhook loaded", style="bright_green")
    else:
        wh_status.append("  ✗ ", style="bold yellow")
        wh_status.append("Discord webhook not set  ", style="yellow")
        wh_status.append("(set DISCORD_WEBHOOK_URL env var)", style="dim yellow")

    console.print(
        Panel(
            api_status + Text("\n") + wh_status,
            border_style="bright_cyan",
            box=box.ROUNDED,
            padding=(0, 2),
        )
    )
    console.print()


def ask(question: str, default: str, choices: list[str] | None = None) -> str:
    t = Text()
    t.append("[ ",  style="dim white")
    t.append("? ",  style="bold bright_cyan")
    t.append("] ",  style="dim white")
    t.append(question, style="bold white")
    t.append(f" (default: {default}) ", style="dim white")
    t.append(f"({default})", style="bold bright_cyan")
    t.append(": ", style="dim white")
    console.print(t, end="")
    raw = input().strip()
    if not raw:
        return default
    if choices:
        return raw.lower() if raw.lower() in choices else default
    return raw


def ask_yn(question: str, default: str = "y") -> bool:
    t = Text()
    t.append("[ ",  style="dim white")
    t.append("? ",  style="bold bright_cyan")
    t.append("] ",  style="dim white")
    t.append(question, style="bold white")
    t.append(" [y/n] ", style="dim white")
    t.append(f"({default})", style="bold bright_cyan")
    t.append(": ", style="dim white")
    console.print(t, end="")
    raw = input().strip().lower()
    if raw not in ("y", "n"):
        return default == "y"
    return raw == "y"
