"""Tag parsing and normalisation."""
from __future__ import annotations

import re
from collections import Counter
from typing import Iterable

_VALID_TAG = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


def normalize_tag(tag: str) -> str:
    """Lower-case a tag and turn inner spaces into dashes; reject anything odd."""
    cleaned = tag.strip().lower().replace(" ", "-")
    if not _VALID_TAG.match(cleaned):
        raise ValueError(f"invalid tag: {tag!r}")
    return cleaned


def normalize_tags(tags: Iterable[str]) -> list[str]:
    """Normalise every tag, keeping the given order."""
    return [normalize_tag(tag) for tag in tags]


def parse_tags(text: str) -> list[str]:
    """Parse a comma-separated tag list such as ``"work, Home Office"``."""
    return normalize_tags(part for part in text.split(",") if part.strip())


def tag_counts(todos) -> dict[str, int]:
    """How many todos carry each tag, most common first (ties alphabetical)."""
    counts = Counter(tag for todo in todos for tag in todo.tags)
    return dict(sorted(counts.items(), key=lambda pair: (-pair[1], pair[0])))
