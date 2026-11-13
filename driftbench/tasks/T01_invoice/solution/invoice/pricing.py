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


class UnknownDiscountCode(ValueError):
    """Raised for a discount code that is not recognised."""


PERCENT_CODES = {"SAVE10": Decimal("0.10"), "SAVE20": Decimal("0.20")}
FLAT_CODES = {"FLAT5": Decimal("5.00")}


def apply_discounts(invoice: Invoice, codes) -> Decimal:
    """Total after discount codes: best percentage first, then flat amounts, floored at 0."""
    for code in codes:
        if code not in PERCENT_CODES and code not in FLAT_CODES:
            raise UnknownDiscountCode(code)
    total = sum((item.total() for item in invoice.items), Decimal("0"))
    percents = [PERCENT_CODES[c] for c in codes if c in PERCENT_CODES]
    if percents:
        total = total * (1 - max(percents))
    total -= sum((FLAT_CODES[c] for c in codes if c in FLAT_CODES), Decimal("0"))
    return quantize(max(total, Decimal("0")))


def total_with_tax(invoice: Invoice, codes, rate: Decimal) -> Decimal:
    return apply_tax(apply_discounts(invoice, codes), rate)
