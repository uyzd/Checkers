import random
import string
import os

LETTERS = string.ascii_lowercase
NUMBERS = string.digits

_WORDS: list[str] | None = None


def _get_words() -> list[str]:
    global _WORDS
    if _WORDS is None:
        path = os.path.join(os.path.dirname(__file__), "words.txt")
        try:
            with open(path) as f:
                _WORDS = [w.strip().lower() for w in f
                          if w.strip() and not w.startswith("#")]
        except FileNotFoundError:
            _WORDS = ["swift", "flame", "storm", "blade", "frost"]
    return _WORDS


def generate_random(length: int, charset: str) -> str:
    if not charset:
        charset = LETTERS
    return "".join(random.choices(charset, k=length))


def generate_4l() -> str:
    return "".join(random.choices(LETTERS, k=4))


def generate_4c() -> str:
    parts = random.choices(LETTERS, k=2) + random.choices(NUMBERS, k=2)
    random.shuffle(parts)
    return "".join(parts)


def generate_5n() -> str:
    return "".join(random.choices(NUMBERS, k=5))


def generate_word() -> str:
    return random.choice(_get_words())


def generate_semi(special_chars: frozenset[str]) -> str:
    if not special_chars:
        return generate_4l()
    sp = random.choice(list(special_chars))
    charset = LETTERS + NUMBERS
    parts = list(random.choices(charset, k=3))
    pos = random.randint(1, len(parts))
    parts.insert(pos, sp)
    return "".join(parts)


def generate_username(length: int, charset: str) -> str:
    return generate_random(length, charset)
