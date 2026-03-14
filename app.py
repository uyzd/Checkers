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

from checker import check_xbox_username, post_discord
from utils import generate_username, ask, ask_yn, print_banner

console = Console()


def scan_settings() -> tuple[int, int, str, bool]:
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

    if os.environ.get("DISCORD_WEBHOOK_URL"):
        console.print(Text("  Discord webhook loaded from environment.", style="dim white"))
        console.print()

    charset_parts = []
    if use_letters:
        charset_parts.append("a-z")
    if use_numbers:
        charset_parts.append("0-9")
    charset_label = " + ".join(charset_parts) or "a-z"

    console.print(Rule("[bold bright_cyan]Ready to scan[/]", style="bright_cyan"))
    summary = Text()
    summary.append("  Length: ",  style="dim white")
    summary.append(str(length),   style="bold bright_cyan")
    summary.append("    Count: ", style="dim white")
    summary.append(str(count),    style="bold bright_cyan")
    summary.append("    Charset: ", style="dim white")
    summary.append(charset_label, style="bold bright_cyan")
    console.print(Panel(summary, border_style="bright_cyan", box=box.ROUNDED, padding=(0, 1)))
    console.print()

    go = ask_yn("Start scanning now", "y")
    return length, count, charset, go


def run_scan(length: int, count: int, charset: str) -> list[str]:
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

            available, err = check_xbox_username(username)

            if err == "rate_limit":
                rate_wait = 2.5
                progress.update(task, status="[yellow]⏸[/]", last_user=username)
                continue
            elif err == "no_key":
                console.print()
                t = Text()
                t.append("  [", style="dim")
                t.append("!", style="bold yellow")
                t.append("] XBL_API_KEY not set — add it in Secrets to enable checking.", style="yellow")
                console.print(t)
                return found
            elif err:
                progress.update(task, status="[red]✗[/]", last_user=username)
                checked += 1
                progress.advance(task)
                time.sleep(0.1)
                continue

            if available:
                found.append(username)
                post_discord(username)
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


def show_found(found: list[str]) -> None:
    console.print()
    if not found:
        t = Text()
        t.append("  [", style="dim")
        t.append("i", style="cyan")
        t.append("] No available usernames found in this scan.", style="dim white")
        console.print(t)
        return

    console.print(Rule(f"[bold bright_green]Found {len(found)} Available Username(s)[/]", style="bright_green"))
    console.print()

    table = Table(box=box.SIMPLE, border_style="dim white", show_header=False, padding=(0, 3))
    table.add_column("Username", style="bold bright_green")
    table.add_column("Length",   style="dim cyan")
    table.add_column("Webhook",  style="dim white")

    wh_note = "✓ posted to Discord" if os.environ.get("DISCORD_WEBHOOK_URL") else "—"
    for u in found:
        table.add_row(u, f"{len(u)} chars", wh_note)

    console.print(table)
    console.print()


def main() -> None:
    print_banner()

    while True:
        length, count, charset, go = scan_settings()

        if not go:
            console.print()
            t = Text()
            t.append("  [", style="dim")
            t.append("i", style="cyan")
            t.append("] Scan cancelled.", style="dim white")
            console.print(t)
            console.print()
            continue

        found = run_scan(length, count, charset)
        show_found(found)

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
