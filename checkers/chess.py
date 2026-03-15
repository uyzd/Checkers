import requests
from utils.proxy import proxy_manager

ENDPOINT = "https://chess.com/member/{}"


def check_chess_username(username: str) -> tuple[bool | None, str | None]:
    try:
        resp = requests.head(
            ENDPOINT.format(username.lower()),
            timeout=8,
            allow_redirects=True,
            proxies=proxy_manager.next(),
        )
        if resp.status_code == 429:
            return None, "rate_limit"
        if resp.status_code == 404:
            return True, None
        return False, None
    except Exception as e:
        return None, str(e)
