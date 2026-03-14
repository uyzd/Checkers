import random
import string


def generate_username(length: int, charset: str) -> str:
    if not charset:
        charset = string.ascii_lowercase
    return "".join(random.choices(charset, k=length))
