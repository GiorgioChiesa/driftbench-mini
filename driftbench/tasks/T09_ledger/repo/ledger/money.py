"""Money helpers. Amounts are stored internally as integer cents."""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

CENT = Decimal("0.01")


def to_cents(amount: Decimal | str | int) -> int:
    """Convert a Decimal, string or int amount to integer cents (rounded half-up)."""
    if isinstance(amount, float):
        raise TypeError("use Decimal or str for money, not float")
    try:
        value = Decimal(str(amount).strip())
    except InvalidOperation:
        raise ValueError(f"invalid amount: {amount!r}") from None
    if not value.is_finite():
        raise ValueError(f"invalid amount: {amount!r}")
    return int(value.quantize(CENT, rounding=ROUND_HALF_UP) * 100)


def from_cents(cents: int) -> Decimal:
    """Convert integer cents back to a Decimal with two decimal places."""
    sign = "-" if cents < 0 else ""
    whole, frac = divmod(abs(cents), 100)
    return Decimal(f"{sign}{whole}.{frac:02d}")


def fmt(cents: int, currency: str = "EUR") -> str:
    """Human-readable amount: ``fmt(123450) == "1,234.50 EUR"``."""
    return f"{from_cents(cents):,} {currency}"
