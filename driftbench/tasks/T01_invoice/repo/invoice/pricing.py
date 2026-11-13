"""Pricing utilities for invoices."""
from decimal import Decimal

from .models import Invoice
from .money import quantize


def subtotal(invoice: Invoice) -> Decimal:
    """Sum of all line totals, rounded to cents."""
    return quantize(sum((item.total() for item in invoice.items), Decimal("0")))


def apply_tax(amount: Decimal, rate: Decimal) -> Decimal:
    """Return amount plus tax at the given rate (e.g. Decimal('0.22'))."""
    if rate < 0:
        raise ValueError("rate must be non-negative")
    return quantize(amount * (1 + rate))
