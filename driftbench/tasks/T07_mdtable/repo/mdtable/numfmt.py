"""Number formatting for table cells."""
from __future__ import annotations

import math
from decimal import ROUND_HALF_UP, Decimal
from typing import Any


def is_number(value: Any) -> bool:
    """True for int, float and Decimal values (bools are not numbers here)."""
    return isinstance(value, (int, float, Decimal)) and not isinstance(value, bool)


def format_number(value: int | float | Decimal, decimals: int | None = None, thousands: str = "") -> str:
    """Format ``value`` without scientific notation.

    With ``decimals`` the value is rounded half-up to exactly that many digits after the point.
    ``thousands`` is an optional separator inserted between groups of three integer digits.
    """
    if not is_number(value):
        raise TypeError(f"not a number: {value!r}")
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return str(value)
    d = Decimal(str(value))
    if decimals is not None:
        if decimals < 0:
            raise ValueError("decimals must be >= 0")
        d = d.quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_UP)
    text = f"{d:f}"
    if thousands:
        sign = "-" if text.startswith("-") else ""
        whole, dot, frac = text.lstrip("-").partition(".")
        text = sign + _group(whole, thousands) + dot + frac
    return text


def percent(value: int | float | Decimal, decimals: int = 1) -> str:
    """Format a ratio as a percentage: ``percent(0.125) == "12.5%"``."""
    return format_number(Decimal(str(value)) * 100, decimals) + "%"


def _group(digits: str, sep: str) -> str:
    groups = []
    while len(digits) > 3:
        groups.insert(0, digits[-3:])
        digits = digits[:-3]
    groups.insert(0, digits)
    return sep.join(groups)
