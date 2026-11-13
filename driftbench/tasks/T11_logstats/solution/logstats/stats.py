"""Aggregate statistics over parsed log records."""
from __future__ import annotations

import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from .endpoints import endpoint_key
from .parser import LogRecord
from .timeutil import floor_minute, parse_iso


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


def percentile(values, p: float) -> float:
    """Nearest-rank percentile: the value at 1-based position ``ceil(p * n / 100)`` of the sorted values."""
    data = sorted(values)
    if not data:
        raise ValueError("percentile of an empty sequence")
    if not 0 < p <= 100:
        raise ValueError(f"p must be in (0, 100], got {p}")
    rank = max(math.ceil(p * len(data) / 100), 1)
    return data[rank - 1]


@dataclass(frozen=True)
class EndpointStats:
    endpoint: str
    count: int
    p50_ms: float | None
    p95_ms: float | None
    error_rate: float


def endpoint_stats(records: Iterable[LogRecord]) -> dict[str, EndpointStats]:
    """Per-endpoint request count, latency percentiles and 5xx error rate."""
    groups: dict[str, list[LogRecord]] = defaultdict(list)
    for r in records:
        groups[endpoint_key(r)].append(r)
    result = {}
    for key, recs in groups.items():
        durations = [r.duration_ms for r in recs if r.duration_ms is not None]
        errors = sum(1 for r in recs if r.status >= 500)
        result[key] = EndpointStats(
            endpoint=key,
            count=len(recs),
            p50_ms=percentile(durations, 50) if durations else None,
            p95_ms=percentile(durations, 95) if durations else None,
            error_rate=round(errors / len(recs), 4),
        )
    return result


def slowest_endpoints(records: Iterable[LogRecord], n: int = 5) -> list[EndpointStats]:
    """The ``n`` endpoints with the highest p95 latency (ties: endpoint key ascending)."""
    if n <= 0:
        return []
    timed = [s for s in endpoint_stats(records).values() if s.p95_ms is not None]
    return sorted(timed, key=lambda s: (-s.p95_ms, s.endpoint))[:n]


def _bound(value):
    if value is None:
        return None
    if isinstance(value, str):
        return parse_iso(value)
    if value.tzinfo is None:
        raise ValueError("window bounds must be timezone-aware")
    return value


def filter_window(records: Iterable[LogRecord], start=None, end=None) -> list[LogRecord]:
    """Records with ``start <= time < end``; a ``None`` bound is open."""
    lo, hi = _bound(start), _bound(end)
    return [r for r in records if (lo is None or r.time >= lo) and (hi is None or r.time < hi)]
