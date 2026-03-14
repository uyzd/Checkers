import os
import requests

XBL_SEARCH_API = "https://xbl.io/api/v2/search/{}"


def check_xbox_username(username: str) -> tuple[bool | None, str | None]:
    api_key = os.environ.get("XBL_API_KEY", "")
    if not api_key:
        return None, "no_key"
    try:
        resp = requests.get(
            XBL_SEARCH_API.format(requests.utils.quote(username)),
            headers={"X-Authorization": api_key, "Accept": "application/json"},
            timeout=8,
        )
        if resp.status_code == 404:
            return True, None
        if resp.status_code == 429:
            return None, "rate_limit"
        if resp.status_code == 200:
            people = resp.json().get("people", [])
            for person in people:
                if person.get("gamertag", "").lower() == username.lower():
                    return False, None
            return True, None
        return None, f"http_{resp.status_code}"
    except Exception as e:
        return None, str(e)
