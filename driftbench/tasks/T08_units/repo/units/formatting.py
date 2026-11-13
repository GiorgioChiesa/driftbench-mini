"""Human-friendly formatting of values with SI prefixes."""
from __future__ import annotations

from .quantity import Quantity

_PREFIXES = [(1e9, "G"), (1e6, "M"), (1e3, "k")]


def si_prefix(value: float) -> tuple[float, str]:
    """Scale ``value`` down by the largest SI prefix it reaches: ``(1.5, "k")`` for 1500."""
    for scale, prefix in _PREFIXES:
        if abs(value) >= scale:
            return value / scale, prefix
    return value, ""


def humanize(value: float, unit: str, precision: int = 3) -> str:
    """``humanize(1500, "m") == "1.5 km"`` (``precision`` significant digits)."""
    scaled, prefix = si_prefix(value)
    return f"{scaled:.{precision}g} {prefix}{unit}"


def format_quantity(q: Quantity, decimals: int = 2) -> str:
    """Fixed-point rendering: ``format_quantity(Quantity(3.14159, "m")) == "3.14 m"``."""
    return f"{q.value:.{decimals}f} {q.unit}"
