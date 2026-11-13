"""Word counting."""
from collections import Counter

from .tokenize import tokenize


def word_counts(text: str) -> Counter:
    return Counter(tokenize(text))


def unique_words(text: str) -> list:
    return sorted(set(tokenize(text)))
