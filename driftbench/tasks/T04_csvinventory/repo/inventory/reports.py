"""Stock reports built from item lists."""
from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Iterable

from .models import Item, round_cents


def total_value(items: Iterable[Item]) -> Decimal:
    """Value of everything on hand, at cost."""
    return round_cents(sum((item.unit_cost * item.on_hand for item in items), Decimal("0")))


def value_by_supplier(items: Iterable[Item]) -> dict[str, Decimal]:
    """Stock value per supplier (alphabetical); items without one go under ``UNASSIGNED``."""
    totals: dict[str, Decimal] = defaultdict(Decimal)
    for item in items:
        totals[item.supplier or "UNASSIGNED"] += item.unit_cost * item.on_hand
    return {supplier: round_cents(totals[supplier]) for supplier in sorted(totals)}


def low_stock(items: Iterable[Item], threshold: int) -> list[Item]:
    """Items whose available stock is below ``threshold``, lowest first."""
    return sorted((item for item in items if item.available < threshold),
                  key=lambda item: (item.available, item.sku))


def out_of_stock(items: Iterable[Item]) -> list[str]:
    return sorted(item.sku for item in items if item.available == 0)


def stock_summary(items: Iterable[Item]) -> dict:
    items = list(items)
    return {
        "skus": len(items),
        "units": sum(item.on_hand for item in items),
        "value": total_value(items),
        "out_of_stock": len(out_of_stock(items)),
    }
