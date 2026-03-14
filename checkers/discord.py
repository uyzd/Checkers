import os
import datetime
import requests


def post_discord(username: str) -> None:
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL", "")
    if not webhook_url:
        return
    try:
        requests.post(
            webhook_url,
            json={
                "content": None,
                "embeds": [
                    {
                        "title": "✅ Available Xbox Username Found",
                        "description": f"**`{username}`**",
                        "color": 0x107C10,
                        "footer": {"text": "Xbox Username Scanner"},
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
