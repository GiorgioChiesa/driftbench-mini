"""Aggregate statistics over parsed log records."""
from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Iterable

from .parser import LogRecord
from .timeutil import floor_minute


def count_by_status(records: Iterable[LogRecord]) -> dict[int, int]:
    return dict(sorted(Counter(r.status for r in records).items()))


def status_classes(records: Iterable[LogRecord]) -> dict[str, int]:
    """Counts per status class: ``{'2xx': 10, '4xx': 2, ...}``."""
    return dict(sorted(Counter(f"{r.status // 100}xx" for r in records).items()))


def top_ips(records: Iterable[LogRecord], n: int = 5) -> list[tuple[str, int]]:
    """The ``n`` busiest client IPs, by request count (ties: IP ascending)."""
    counts = Counter(r.ip for r in records)
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:n]


def total_bytes(records: Iterable[LogRecord]) -> int:
    return sum(r.size for r in records)


def requests_per_minute(records: Iterable[LogRecord]) -> dict[datetime, int]:
    """Request counts per UTC minute, in chronological order."""
    return dict(sorted(Counter(floor_minute(r.time) for r in records).items()))
