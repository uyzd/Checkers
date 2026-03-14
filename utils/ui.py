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

    def key_row(label: str, env_var: str, color: str = "bright_green") -> Text:
        val = os.environ.get(env_var, "")
        t = Text()
        if val:
            t.append("  ✓ ", style="bold bright_green")
            t.append(f"{label} loaded", style=color)
        else:
            t.append("  ✗ ", style="bold red")
            t.append(f"{label} not set  ", style="red")
            t.append(f"(set {env_var})", style="dim yellow")
        return t

    steam_row = Text()
    if os.environ.get("STEAM_API_KEY", ""):
        steam_row.append("  ✓ ", style="bold bright_green")
        steam_row.append("Steam API key loaded", style="bright_blue")
    else:
        steam_row.append("  ✓ ", style="bold bright_green")
        steam_row.append("Steam  ", style="bright_blue")
        steam_row.append("(no key needed — uses public profiles)", style="dim cyan")

    rows = (
        key_row("xbl.io API key",        "XBL_API_KEY")
        + Text("\n")
        + steam_row
        + Text("\n")
        + key_row("Discord webhook (Xbox channel)",  "DISCORD_WEBHOOK_URL",  "bright_magenta")
        + Text("\n")
        + key_row("Discord webhook (Steam channel)", "STEAM_WEBHOOK_URL",    "bright_blue")
    )

    console.print(
        Panel(
            rows,
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
