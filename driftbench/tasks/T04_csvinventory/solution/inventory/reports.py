"""Stock reports built from item lists."""
from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Iterable, NamedTuple

from . import csvio
from .models import Item, round_cents

REORDER_HEADER = ("supplier", "sku", "name", "available", "order_qty", "cost")
UNASSIGNED = "UNASSIGNED"


class ReorderLine(NamedTuple):
    supplier: str
    sku: str
    name: str
    available: int
    order_qty: int
    cost: Decimal


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


def needs_reorder(item: Item) -> bool:
    """True when the item has a reorder point and available stock is at or below it."""
    return item.reorder_point > 0 and item.available <= item.reorder_point


def order_quantity(item: Item) -> int:
    """Units to order to bring available stock up to twice the reorder point."""
    if not needs_reorder(item):
        return 0
    needed = 2 * item.reorder_point - item.available
    if item.reorder_qty > 0:
        packs = -(-needed // item.reorder_qty)  # ceiling division
        needed = packs * item.reorder_qty
    return needed


def reorder_report(items: Iterable[Item]) -> list[ReorderLine]:
    """One line per item to reorder, sorted by supplier then SKU."""
    lines = []
    for item in items:
        if needs_reorder(item):
            qty = order_quantity(item)
            lines.append(ReorderLine(item.supplier, item.sku, item.name, item.available, qty,
                                     round_cents(item.unit_cost * qty)))
    return sorted(lines, key=lambda line: (line.supplier, line.sku))


def group_by_supplier(lines: Iterable[ReorderLine]) -> dict[str, list[ReorderLine]]:
    """Reorder lines per supplier, suppliers in alphabetical order."""
    groups: dict[str, list[ReorderLine]] = defaultdict(list)
    for line in lines:
        groups[line.supplier or UNASSIGNED].append(line)
    return {supplier: groups[supplier] for supplier in sorted(groups)}


def supplier_totals(lines: Iterable[ReorderLine]) -> dict[str, Decimal]:
    """Total reorder cost per supplier (same keys and order as ``group_by_supplier``)."""
    return {supplier: round_cents(sum((line.cost for line in group), Decimal("0")))
            for supplier, group in group_by_supplier(lines).items()}


def export_reorder_csv(lines: Iterable[ReorderLine], path) -> int:
    """Write the reorder report as CSV; returns the number of data rows."""
    return csvio.write_rows(path, REORDER_HEADER, (tuple(line) for line in lines))
