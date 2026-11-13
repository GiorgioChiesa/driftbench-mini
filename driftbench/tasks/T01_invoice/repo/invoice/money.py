"""Money helpers shared across the package."""
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")


def quantize(amount: Decimal) -> Decimal:
    """Round an amount to cents."""
    return Decimal(amount).quantize(CENT, rounding=ROUND_HALF_UP)


def fmt(amount: Decimal) -> str:
    """Format an amount for display, e.g. 1234.5 -> '1,234.50'."""
    return f"{quantize(amount):,.2f}"
