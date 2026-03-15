import os
import requests

DISCORD_ME            = "https://discord.com/api/v10/users/@me"
DISCORD_RELATIONSHIPS = "https://discord.com/api/v10/users/@me/relationships"
DISCORD_REL_DELETE    = "https://discord.com/api/v10/users/@me/relationships/{}"

_me_username: str | None = None


def _headers() -> dict | None:
    token = os.environ.get("DISCORD_TOKEN", "")
    return {"Authorization": token, "Content-Type": "application/json"} if token else None


def _resolve_me(hdrs: dict) -> str | None:
    global _me_username
    if _me_username is not None:
        return _me_username
    try:
        r = requests.get(DISCORD_ME, headers=hdrs, timeout=6)
        if r.status_code == 200:
            _me_username = r.json().get("username", "").lower()
            return _me_username
    except Exception:
        pass
    return None


def _cancel_request(hdrs: dict, username: str) -> None:
    """Delete outgoing pending friend request (type 4) to the given username."""
    try:
        r = requests.get(DISCORD_RELATIONSHIPS, headers=hdrs, timeout=6)
        if r.status_code != 200:
            return
        for rel in r.json():
            if (
                rel.get("type") == 4
                and rel.get("user", {}).get("username", "").lower() == username.lower()
            ):
                requests.delete(
                    DISCORD_REL_DELETE.format(rel["id"]),
                    headers=hdrs,
                    timeout=6,
                )
                break
    except Exception:
        pass


def check_discord_username(username: str) -> tuple[bool | None, str | None]:
    hdrs = _headers()
    if not hdrs:
        return None, "no_key"

    try:
        me = _resolve_me(hdrs)
        if me is None:
            return None, "invalid_token"

        if me == username.lower():
            return False, None

        r = requests.post(
            DISCORD_RELATIONSHIPS,
            json={"username": username},
            headers=hdrs,
            timeout=8,
        )

        if r.status_code == 429:
            return None, "rate_limit"

        if r.status_code == 204:
            _cancel_request(hdrs, username)
            return False, None

        if r.status_code in (200, 201):
            return False, None

        if r.status_code == 400:
            body = r.json() if r.content else {}
            code = body.get("code", 0)
            message = body.get("message", "")
            errors  = str(body.get("errors", ""))
            if (
                code == 80004
                or "Unknown User" in message
                or "username" in errors.lower()
            ):
                return True, None
            return None, f"discord_{code or r.status_code}"

        if r.status_code == 401:
            return None, "invalid_token"

        return None, f"http_{r.status_code}"

    except Exception as e:
        return None, str(e)
