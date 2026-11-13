"""Parsing of human-friendly rate specifications such as ``"10/min"`` or ``"5/30s"``."""
from __future__ import annotations

import re
from dataclasses import dataclass

_UNITS = {
    "s": 1.0, "sec": 1.0, "second": 1.0,
    "m": 60.0, "min": 60.0, "minute": 60.0,
    "h": 3600.0, "hour": 3600.0,
    "d": 86400.0, "day": 86400.0,
}
_SPEC = re.compile(r"^\s*(\d+)\s*/\s*(\d*(?:\.\d+)?)\s*([a-z]+)\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class Rate:
    """``limit`` events per ``window`` seconds."""

    limit: int
    window: float

    @property
    def per_second(self) -> float:
        return self.limit / self.window


def parse_rate(spec: str) -> Rate:
    """Parse ``"<count>/<multiplier?><unit>"``, e.g. ``"10/min"``, ``"5/30s"`` or ``"100/h"``."""
    match = _SPEC.match(spec)
    if not match:
        raise ValueError(f"invalid rate spec: {spec!r}")
    count, multiplier, unit = match.groups()
    unit = unit.lower()
    if unit not in _UNITS:
        raise ValueError(f"unknown time unit {unit!r} in {spec!r}")
    window = float(multiplier or 1) * _UNITS[unit]
    limit = int(count)
    if limit <= 0 or window <= 0:
        raise ValueError(f"rate must be positive: {spec!r}")
    return Rate(limit=limit, window=window)
