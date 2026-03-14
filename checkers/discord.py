import os
import datetime
import requests

PLATFORM_WEBHOOK_CONFIG: dict[str, tuple[str, str, int, str]] = {
    "xbox": (
        "DISCORD_WEBHOOK_URL",
        "✅ Available Xbox Username Found",
        0x107C10,
        "Xbox Username Scanner",
    ),
    "steam": (
        "STEAM_WEBHOOK_URL",
        "✅ Available Steam Username Found",
        0x1B2838,
        "Steam Username Scanner",
    ),
    "roblox": (
        "ROBLOX_WEBHOOK_URL",
        "✅ Available Roblox Username Found",
        0xFF3E3E,
        "Roblox Username Scanner",
    ),
}


def post_platform_discord(username: str, platform: str) -> None:
    config = PLATFORM_WEBHOOK_CONFIG.get(platform)
    if not config:
        return
    env_var, title, color, footer = config
    webhook_url = os.environ.get(env_var, "")
    if not webhook_url:
        return
    try:
        requests.post(
            webhook_url,
            json={
                "content": None,
                "embeds": [
                    {
                        "title": title,
                        "description": f"**`{username}`**",
                        "color": color,
                        "footer": {"text": footer},
                        "timestamp": datetime.datetime.now(
                            datetime.timezone.utc
                        ).isoformat(),
                    }
                ],
            },
            timeout=5,
        )
    except Exception:
        pass


def post_discord(username: str) -> None:
    post_platform_discord(username, "xbox")
