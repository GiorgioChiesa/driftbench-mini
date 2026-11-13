"""Sanity checks run on inventory data before it is imported."""
from __future__ import annotations

import re
from collections import Counter
from typing import Iterable

from .models import Item

SKU_PATTERN = re.compile(r"^[A-Z]{1,4}-\d{3,5}$")


class InvalidSku(ValueError):
    """Raised for SKUs that do not follow the ``ABC-1234`` convention."""


def validate_sku(sku: str) -> str:
    if not SKU_PATTERN.match(sku):
        raise InvalidSku(f"invalid SKU: {sku!r}")
    return sku


def item_problems(item: Item) -> list[str]:
    """Human-readable list of everything that looks wrong with ``item``."""
    problems = []
    try:
        validate_sku(item.sku)
    except InvalidSku as exc:
        problems.append(str(exc))
    if item.unit_cost < 0:
        problems.append("negative unit cost")
    if item.reserved > item.on_hand:
        problems.append("reserved exceeds on hand")
    if item.reorder_qty and not item.reorder_point:
        problems.append("reorder_qty set without reorder_point")
    return problems


def find_duplicates(items: Iterable[Item]) -> list[str]:
    """SKUs that appear more than once, sorted."""
    counts = Counter(item.sku for item in items)
    return sorted(sku for sku, count in counts.items() if count > 1)
