"""Date helpers shared by the models and the renderers."""
from __future__ import annotations

from datetime import date, datetime

ISO_FORMAT = "%Y-%m-%d"


def parse_iso_date(text: str) -> date:
    """Parse a ``YYYY-MM-DD`` string (surrounding whitespace is ignored)."""
    return datetime.strptime(text.strip(), ISO_FORMAT).date()


def format_date(value: date | None) -> str:
    """Render a date as ``YYYY-MM-DD``; ``None`` becomes ``"-"``."""
    return value.strftime(ISO_FORMAT) if value is not None else "-"


def days_between(start: date, end: date) -> int:
    """Signed number of days from ``start`` to ``end``."""
    return (end - start).days


def humanize_age(created: date, today: date) -> str:
    """Describe how long ago ``created`` was, relative to ``today``."""
    days = days_between(created, today)
    if days < 0:
        raise ValueError("created date is in the future")
    if days == 0:
        return "today"
    if days == 1:
        return "yesterday"
    return f"{days} days ago"
