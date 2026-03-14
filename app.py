import sys
import os
import time
import string

from rich.console import Console
from rich.text import Text
from rich.rule import Rule
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn

from checker import check_xbox_username, check_steam_username, post_platform_discord
from utils import generate_username, ask, ask_yn, print_banner

console = Console()

PLATFORM_CHECKERS = {
    "xbox":  check_xbox_username,
    "steam": check_steam_username,
}

PLATFORM_KEY_VARS = {
    "xbox":  "XBL_API_KEY",
    "steam": "STEAM_API_KEY",
}

PLATFORM_COLORS = {
    "xbox":  "bright_green",
    "steam": "bright_blue",
}

PLATFORM_LABELS = {
    "xbox":  "Xbox",
    "steam": "Steam",
}


def scan_settings() -> tuple[int, int, str, list[str], bool]:
    console.print(Rule("[bold bright_cyan]Scan Settings[/]", style="bright_cyan"))
    console.print()

    raw_len = ask("Username length", "4")
    try:
        length = max(1, min(16, int(raw_len)))
    except ValueError:
        length = 4

    raw_count = ask("How many usernames to check", "20")
    try:
        count = max(1, int(raw_count))
    except ValueError:
        count = 20

    console.print()
    console.print(Text("  Platforms to check:", style="dim white"))
    platforms: list[str] = []
    for pid, label in PLATFORM_LABELS.items():
        if pid == "steam":
            default = "y"
        else:
            key_set = bool(os.environ.get(PLATFORM_KEY_VARS.get(pid, ""), ""))
            default = "y" if key_set else "n"
        if ask_yn(f"Check {label}", default):
            platforms.append(pid)

    if not platforms:
        platforms = ["xbox"]

    console.print()
    console.print(Text("  Character set to use:", style="dim white"))
    use_letters = ask_yn("Include letters (a-z)", "y")
    use_numbers = ask_yn("Include numbers (0-9)", "y")
    console.print()

    charset = ""
    if use_letters:
        charset += string.ascii_lowercase
    if use_numbers:
        charset += string.digits
    if not charset:
        charset = string.ascii_lowercase

    WEBHOOK_VARS   = {"xbox": "DISCORD_WEBHOOK_URL", "steam": "STEAM_WEBHOOK_URL"}
    WEBHOOK_LABELS = {"xbox": "Discord webhook (Xbox channel)", "steam": "Discord webhook (Steam channel)"}
    for pid in platforms:
        env_var = WEBHOOK_VARS.get(pid, "")
        label   = WEBHOOK_LABELS.get(pid, pid)
        t = Text()
        if os.environ.get(env_var, ""):
            t.append("  ✓ ", style="bold bright_green")
            t.append(f"{label} loaded", style="dim white")
        else:
            t.append("  ✗ ", style="dim yellow")
            t.append(f"{label} not set ", style="dim yellow")
            t.append(f"(set {env_var})", style="dim")
        console.print(t)
    console.print()

    charset_parts = []
    if use_letters:
        charset_parts.append("a-z")
    if use_numbers:
        charset_parts.append("0-9")
    charset_label = " + ".join(charset_parts) or "a-z"

    platform_label = " + ".join(PLATFORM_LABELS[p] for p in platforms)

    console.print(Rule("[bold bright_cyan]Ready to scan[/]", style="bright_cyan"))
    summary = Text()
    summary.append("  Length: ",    style="dim white")
    summary.append(str(length),     style="bold bright_cyan")
    summary.append("    Count: ",   style="dim white")
    summary.append(str(count),      style="bold bright_cyan")
    summary.append("    Charset: ", style="dim white")
    summary.append(charset_label,   style="bold bright_cyan")
    summary.append("    Platforms: ", style="dim white")
    summary.append(platform_label,  style="bold bright_cyan")
    console.print(Panel(summary, border_style="bright_cyan", box=box.ROUNDED, padding=(0, 1)))
    console.print()

    go = ask_yn("Start scanning now", "y")
    return length, count, charset, platforms, go


def run_scan(length: int, count: int, charset: str, platforms: list[str]) -> list[str]:
    found: list[str] = []
    checked = 0
    seen: set[str] = set()

    console.print(Rule("[bold bright_cyan]Scanning Usernames[/]", style="bright_cyan"))
    console.print()

    with Progress(
        TextColumn("  "),
        TextColumn("{task.fields[status]}"),
        TextColumn("[bold bright_cyan]{task.fields[last_user]}[/]"),
        BarColumn(bar_width=28, style="bright_cyan", complete_style="bright_green"),
        TextColumn("[dim white]{task.completed}/{task.total}[/]"),
        TextColumn("[bold bright_green]| {task.fields[found_count]} found[/]"),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    ) as progress:
        task = progress.add_task(
            "scan",
            total=count,
            status="[dim]~[/]",
            last_user="",
            found_count=0,
        )
        rate_wait = 0

        while checked < count:
            if rate_wait > 0:
                time.sleep(rate_wait)
                rate_wait = 0

            username = generate_username(length, charset)
            while username in seen:
                username = generate_username(length, charset)
            seen.add(username)

            all_available = True
            had_error = False

            for pid in platforms:
                checker_fn = PLATFORM_CHECKERS[pid]
                available, err = checker_fn(username)

                if err == "rate_limit":
                    rate_wait = 2.5
                    progress.update(task, status="[yellow]⏸[/]", last_user=username)
                    had_error = True
                    break
                elif err == "no_key":
                    label = PLATFORM_LABELS[pid]
                    var   = PLATFORM_KEY_VARS[pid]
                    console.print()
                    t = Text()
                    t.append("  [", style="dim")
                    t.append("!", style="bold yellow")
                    t.append(f"] {label}: {var} not set — skipping platform.", style="yellow")
                    console.print(t)
                    platforms = [p for p in platforms if p != pid]
                    if not platforms:
                        return found
                    had_error = True
                    break
                elif err:
                    progress.update(task, status="[red]✗[/]", last_user=username)
                    had_error = True
                    break
                elif not available:
                    all_available = False
                    break

            if had_error:
                if rate_wait == 0:
                    checked += 1
                    progress.advance(task)
                    time.sleep(0.1)
                continue

            if all_available:
                found.append(username)
                for pid in platforms:
                    post_platform_discord(username, pid)
                progress.update(
                    task,
                    status="[bold bright_green]✓[/]",
                    last_user=username,
                    found_count=len(found),
                )
            else:
                progress.update(task, status="[dim red]✗[/]", last_user=username)

            checked += 1
            progress.advance(task)
            time.sleep(0.05)

    return found


def show_found(found: list[str], platforms: list[str]) -> None:
    console.print()
    if not found:
        t = Text()
        t.append("  [", style="dim")
        t.append("i", style="cyan")
        t.append("] No available usernames found in this scan.", style="dim white")
        console.print(t)
        return

    platform_label = " + ".join(PLATFORM_LABELS[p] for p in platforms)
    console.print(Rule(
        f"[bold bright_green]Found {len(found)} Available on {platform_label}[/]",
        style="bright_green",
    ))
    console.print()

    table = Table(box=box.SIMPLE, border_style="dim white", show_header=False, padding=(0, 3))
    table.add_column("Username",  style="bold bright_green")
    table.add_column("Length",    style="dim cyan")
    table.add_column("Platforms", style="dim white")
    table.add_column("Webhook",   style="dim white")

    WEBHOOK_VARS = {"xbox": "DISCORD_WEBHOOK_URL", "steam": "STEAM_WEBHOOK_URL"}
    posted_to = [p.title() for p in platforms if os.environ.get(WEBHOOK_VARS.get(p, ""), "")]
    wh_note = ("✓ " + ", ".join(posted_to)) if posted_to else "—"
    for u in found:
        table.add_row(
            u,
            f"{len(u)} chars",
            platform_label,
            wh_note,
        )

    console.print(table)
    console.print()


def main() -> None:
    print_banner()

    while True:
        length, count, charset, platforms, go = scan_settings()

        if not go:
            console.print()
            t = Text()
            t.append("  [", style="dim")
            t.append("i", style="cyan")
            t.append("] Scan cancelled.", style="dim white")
            console.print(t)
            console.print()
            continue

        found = run_scan(length, count, charset, platforms)
        show_found(found, platforms)

        if not ask_yn("Run another scan", "y"):
            console.print()
            t = Text()
            t.append("  [", style="dim")
            t.append("✓", style="bright_green")
            t.append("] Done. Goodbye.", style="white")
            console.print(t)
            console.print()
            sys.exit(0)

        print_banner()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print()
        t = Text()
        t.append("\n  [", style="dim")
        t.append("✓", style="bright_green")
        t.append("] Interrupted. Goodbye.", style="white")
        console.print(t)
        console.print()
        sys.exit(0)
