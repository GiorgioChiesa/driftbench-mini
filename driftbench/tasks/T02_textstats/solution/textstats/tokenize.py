"""Word tokenization."""
import re

WORD_RE = re.compile(r"[a-z]+(?:'[a-z]+)?")


def tokenize(text: str) -> list:
    """Split text into lowercase word tokens (contractions kept whole)."""
    return WORD_RE.findall(text.lower())
