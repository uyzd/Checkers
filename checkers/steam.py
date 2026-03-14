import os
import requests

STEAM_API        = "https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/"
STEAM_PROFILE    = "https://steamcommunity.com/id/{}/?xml=1"
NOT_FOUND_MARKER = b"The specified profile could not be found."


def check_steam_username(username: str) -> tuple[bool | None, str | None]:
    api_key = os.environ.get("STEAM_API_KEY", "")
    if api_key:
        return _check_via_api(username, api_key)
    return _check_via_profile(username)


def _check_via_api(username: str, api_key: str) -> tuple[bool | None, str | None]:
    try:
        resp = requests.get(
            STEAM_API,
            params={"key": api_key, "vanityurl": username},
            timeout=8,
        )
        if resp.status_code == 429:
            return None, "rate_limit"
        if resp.status_code != 200:
            return None, f"http_{resp.status_code}"
        success = resp.json().get("response", {}).get("success")
        if success == 1:
            return False, None
        if success == 42:
            return True, None
        return None, f"steam_error_{success}"
    except Exception as e:
        return None, str(e)


def _check_via_profile(username: str) -> tuple[bool | None, str | None]:
    try:
        resp = requests.get(
            STEAM_PROFILE.format(username),
            timeout=8,
            headers={"User-Agent": "Mozilla/5.0"},
            allow_redirects=True,
        )
        if resp.status_code == 429:
            return None, "rate_limit"
        if resp.status_code not in (200, 404):
            return None, f"http_{resp.status_code}"
        if NOT_FOUND_MARKER in resp.content:
            return True, None
        return False, None
    except Exception as e:
        return None, str(e)
