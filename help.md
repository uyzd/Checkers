# Xbox Username Scanner — Console App

A colorful terminal console app that scans for available Xbox Live usernames and posts results to Discord.

## Project Structure

```
app.py                  — Main entry: scan loop, settings, progress bar, results
checker/
  __init__.py           — Exports: check_xbox_username, post_discord
  xbox.py               — Xbox availability check via XBL.IO API
  discord.py            — Discord webhook embed posting
utils/
  __init__.py           — Exports: generate_username, ask, ask_yn, print_banner
  generator.py          — Random username generation from charset
  ui.py                 — Rich console helpers: banner, ask(), ask_yn()
wsgi/
  adj.txt               — Adjective word list (legacy, kept for reference)
  noun.txt              — Noun word list (legacy, kept for reference)
```

## Features
- Xbox ASCII art banner (rainbow colors)
- Configurable scan: length, count, charset (a-z / 0-9)
- XBL.IO API for live Xbox availability checking
- Strips `#1234` gamertag suffixes automatically
- Rate-limit handling (auto-pauses on 429)
- Discord webhook: posts each found username as a green embed
- Progress bar: `✓ kv3q ══════ 8/200 | 8 found 0:00:14`
- Loop: asks to run another scan after each batch

## Tech Stack
- Python 3.12
- `rich` — terminal UI, progress bars, panels, tables
- `requests` — HTTP calls

## Environment Variables (set in Secrets tab)
- `XBL_API_KEY` — Free key from https://xbl.io
- `DISCORD_WEBHOOK_URL` — Discord channel webhook URL

## Running
```
python app.py
```
