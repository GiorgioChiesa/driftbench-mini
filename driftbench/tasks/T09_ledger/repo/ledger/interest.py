"""Interest helpers (simple interest, ACT/365 day count)."""
from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from .money import CENT


def days_between(start: date, end: date) -> int:
    """Number of days from ``start`` to ``end``; ``end`` must not precede ``start``."""
    if end < start:
        raise ValueError("end precedes start")
    return (end - start).days


def simple_interest(balance: Decimal, annual_rate: Decimal, days: int) -> Decimal:
    """Interest on ``balance`` over ``days`` days, ACT/365, rounded half-up to cents."""
    if days < 0:
        raise ValueError("days must be >= 0")
    raw = Decimal(balance) * Decimal(annual_rate) * days / 365
    return raw.quantize(CENT, rounding=ROUND_HALF_UP)


def interest_for_period(balance: Decimal, annual_rate: Decimal, start: date, end: date) -> Decimal:
    return simple_interest(balance, annual_rate, days_between(start, end))
