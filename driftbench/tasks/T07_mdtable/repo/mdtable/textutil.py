"""Text measuring and fitting helpers that understand wide (East Asian) characters."""
from __future__ import annotations

import unicodedata

ELLIPSIS = "…"


def char_width(ch: str) -> int:
    """Number of terminal/display columns taken by a single character."""
    if unicodedata.combining(ch):
        return 0
    return 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1


def display_width(text: str) -> int:
    """Number of display columns taken by ``text``."""
    return sum(char_width(ch) for ch in text)


def pad(text: str, width: int, align: str = "l") -> str:
    """Pad ``text`` with spaces to ``width`` display columns.

    ``align`` is ``"l"``, ``"r"`` or ``"c"``; when centring, the odd extra space goes on the
    right. Text that is already wide enough is returned unchanged.
    """
    gap = width - display_width(text)
    if align not in ("l", "r", "c"):
        raise ValueError(f"unknown alignment {align!r}")
    if gap <= 0:
        return text
    if align == "l":
        return text + " " * gap
    if align == "r":
        return " " * gap + text
    left = gap // 2
    return " " * left + text + " " * (gap - left)


def truncate(text: str, width: int, ellipsis: str = ELLIPSIS) -> str:
    """Shorten ``text`` to at most ``width`` display columns, ending with ``ellipsis`` if cut."""
    if width < display_width(ellipsis):
        raise ValueError("width is too small to fit the ellipsis")
    if display_width(text) <= width:
        return text
    budget = width - display_width(ellipsis)
    kept, used = [], 0
    for ch in text:
        w = char_width(ch)
        if used + w > budget:
            break
        kept.append(ch)
        used += w
    return "".join(kept) + ellipsis
