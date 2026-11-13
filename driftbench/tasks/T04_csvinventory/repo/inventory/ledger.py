"""Stock movements (receipts, shipments, reservations) with an audit trail."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import Item

KINDS = ("receive", "ship", "reserve", "release")


@dataclass(frozen=True)
class Movement:
    sku: str
    kind: str
    quantity: int
    note: str = ""


class Ledger:
    """Applies movements to a set of items and remembers every one of them."""

    def __init__(self, items: Iterable[Item]) -> None:
        self._items = {item.sku: item for item in items}
        self._history: list[Movement] = []

    def item(self, sku: str) -> Item:
        try:
            return self._items[sku]
        except KeyError:
            raise KeyError(f"unknown SKU: {sku}") from None

    def receive(self, sku: str, quantity: int, note: str = "") -> Item:
        item = self._check(sku, quantity)
        item.on_hand += quantity
        return self._record(item, "receive", quantity, note)

    def ship(self, sku: str, quantity: int, note: str = "") -> Item:
        item = self._check(sku, quantity)
        if quantity > item.available:
            raise ValueError(f"{sku}: cannot ship {quantity}, only {item.available} available")
        item.on_hand -= quantity
        return self._record(item, "ship", quantity, note)

    def reserve(self, sku: str, quantity: int, note: str = "") -> Item:
        item = self._check(sku, quantity)
        if quantity > item.available:
            raise ValueError(f"{sku}: cannot reserve {quantity}, only {item.available} available")
        item.reserved += quantity
        return self._record(item, "reserve", quantity, note)

    def release(self, sku: str, quantity: int, note: str = "") -> Item:
        item = self._check(sku, quantity)
        item.reserved -= min(quantity, item.reserved)
        return self._record(item, "release", quantity, note)

    def history(self, sku: str | None = None) -> list[Movement]:
        """Movements in the order they happened, optionally for one SKU only."""
        return [m for m in self._history if sku is None or m.sku == sku]

    def _check(self, sku: str, quantity: int) -> Item:
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError(f"quantity must be a positive integer, got {quantity!r}")
        return self.item(sku)

    def _record(self, item: Item, kind: str, quantity: int, note: str) -> Item:
        self._history.append(Movement(item.sku, kind, quantity, note))
        return item
