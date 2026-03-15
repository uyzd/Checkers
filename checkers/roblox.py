import os
import requests

ROBLOX_API = "https://users.roblox.com/v1/usernames/users"


def check_roblox_username(username: str) -> tuple[bool | None, str | None]:
    cookie = os.environ.get("ROBLOX_COOKIE", "")
    headers = {"Content-Type": "application/json"}
    if cookie:
        headers["Cookie"] = f".ROBLOSECURITY={cookie}"
    try:
        resp = requests.post(
            ROBLOX_API,
            json={"usernames": [username], "excludeBannedUsers": False},
            headers=headers,
            timeout=8,
        )
        if resp.status_code == 429:
            return None, "rate_limit"
        if resp.status_code == 401:
            return None, "invalid_cookie"
        if resp.status_code != 200:
            return None, f"http_{resp.status_code}"
        data = resp.json().get("data", [])
        for entry in data:
            if entry.get("requestedUsername", "").lower() == username.lower():
                return False, None
        return True, None
    except Exception as e:
        return None, str(e)
