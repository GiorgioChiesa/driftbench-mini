"""Word tokenization."""
import re

WORD_RE = re.compile(r"[a-z]+")


def tokenize(text: str) -> list:
    """Split text into lowercase word tokens."""
    return WORD_RE.findall(text.lower())
