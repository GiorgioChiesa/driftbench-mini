"""Word counting."""
from collections import Counter

from .tokenize import tokenize


def word_counts(text: str) -> Counter:
    return Counter(tokenize(text))


def unique_words(text: str) -> list:
    return sorted(set(tokenize(text)))


def top_words(text: str, n: int, stopwords=None) -> list:
    from .stopwords import DEFAULT_STOPWORDS
    if n <= 0:
        raise ValueError("n must be positive")
    stop = DEFAULT_STOPWORDS if stopwords is None else set(stopwords)
    counts = Counter(t for t in tokenize(text) if t not in stop)
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:n]
