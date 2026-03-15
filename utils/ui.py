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
    sub.append("Username Scanner", style="bold bright_green")
    sub.append("  ·  ", style="dim white")
    sub.append("Xbox · Steam · Roblox · Discord  →  posts to Discord", style="dim cyan")
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

    def optional_row(label: str, env_var: str, no_key_note: str, color: str) -> Text:
        t = Text()
        if os.environ.get(env_var, ""):
            t.append("  ✓ ", style="bold bright_green")
            t.append(f"{label} loaded", style=color)
        else:
            t.append("  ✓ ", style="bold bright_green")
            t.append(f"{label}  ", style=color)
            t.append(f"({no_key_note})", style="dim cyan")
        return t

    rows = (
        key_row("xbl.io API key",                    "XBL_API_KEY")
        + Text("\n")
        + optional_row("Steam",   "STEAM_API_KEY",  "no key needed — uses public profiles", "bright_blue")
        + Text("\n")
        + optional_row("Roblox",  "ROBLOX_COOKIE",  "no key needed — optional cookie for rate limits", "bright_red")
        + Text("\n")
        + key_row("Discord token",                   "DISCORD_TOKEN",           "light_violet")
        + Text("\n")
        + key_row("Discord webhook (Xbox channel)",   "DISCORD_WEBHOOK_URL",     "bright_magenta")
        + Text("\n")
        + key_row("Discord webhook (Steam channel)",  "STEAM_WEBHOOK_URL",       "bright_blue")
        + Text("\n")
        + key_row("Discord webhook (Roblox channel)", "ROBLOX_WEBHOOK_URL",      "bright_red")
        + Text("\n")
        + key_row("Discord webhook (Discord channel)","DISCORD_WEBHOOK_URL_DC",  "light_violet")
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


def ask_choice(question: str, options: list[tuple[str, str]], default: str) -> str:
    t = Text()
    t.append(f"\n  {question}\n", style="bold white")
    console.print(t)
    for key, desc in options:
        mark = "bold bright_cyan" if key == default else "dim white"
        row = Text()
        row.append(f"    [{key}] ", style=mark)
        row.append(desc, style="dim white" if key != default else "white")
        console.print(row)
    console.print()
    t2 = Text()
    t2.append("[ ",  style="dim white")
    t2.append("? ",  style="bold bright_cyan")
    t2.append("] ",  style="dim white")
    t2.append("Choose mode", style="bold white")
    t2.append(f" ({default})", style="bold bright_cyan")
    t2.append(": ", style="dim white")
    console.print(t2, end="")
    raw = input().strip().lower()
    valid = {k for k, _ in options}
    return raw if raw in valid else default


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
