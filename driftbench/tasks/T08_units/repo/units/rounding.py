"""Rounding helpers for presenting measured values."""
from __future__ import annotations

import math


def round_sig(x: float, digits: int = 3) -> float:
    """Round ``x`` to ``digits`` significant digits."""
    if digits < 1:
        raise ValueError("digits must be >= 1")
    magnitude = math.floor(math.log10(abs(x)))
    return round(x, digits - 1 - magnitude)


def round_to_step(x: float, step: float) -> float:
    """Round ``x`` to the nearest multiple of ``step``."""
    if step <= 0:
        raise ValueError("step must be positive")
    return round(x / step) * step


def clamp(x: float, lo: float, hi: float) -> float:
    if lo > hi:
        raise ValueError("lo must not exceed hi")
    return max(lo, min(hi, x))
