"""Readability metrics (rough heuristics)."""
import re

from .tokenize import tokenize

SENTENCE_END = re.compile(r"[.!?]+")
VOWEL_GROUPS = re.compile(r"[aeiouy]+")


def count_sentences(text: str) -> int:
    return len([s for s in SENTENCE_END.split(text) if s.strip()])


def syllables(word: str) -> int:
    groups = VOWEL_GROUPS.findall(word.lower())
    n = len(groups)
    if word.lower().endswith("e") and n > 1:
        n -= 1
    return max(n, 1)


def avg_sentence_length(text: str) -> float:
    return len(tokenize(text)) / count_sentences(text)


def flesch_reading_ease(text: str) -> float:
    words = tokenize(text)
    if not words:
        return 0.0
    syl = sum(syllables(w) for w in words)
    return 206.835 - 1.015 * avg_sentence_length(text) - 84.6 * (syl / len(words))
