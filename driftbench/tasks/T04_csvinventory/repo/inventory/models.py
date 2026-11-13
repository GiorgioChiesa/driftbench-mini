"""Inventory data model."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

CENTS = Decimal("0.01")


def round_cents(value: Decimal) -> Decimal:
    """Round a money amount to cents, half up (the accounting convention)."""
    return Decimal(value).quantize(CENTS, rounding=ROUND_HALF_UP)


@dataclass
class Item:
    sku: str
    name: str
    supplier: str = ""
    on_hand: int = 0
    reserved: int = 0
    unit_cost: Decimal = Decimal("0.00")
    reorder_point: int = 0
    reorder_qty: int = 0

    def __post_init__(self) -> None:
        self.sku = self.sku.strip()
        self.supplier = (self.supplier or "").strip()
        self.on_hand = int(self.on_hand)
        self.reserved = int(self.reserved)
        self.reorder_point = int(self.reorder_point)
        self.reorder_qty = int(self.reorder_qty)
        self.unit_cost = Decimal(str(self.unit_cost))
        if self.on_hand < 0 or self.reserved < 0:
            raise ValueError(f"{self.sku}: stock levels cannot be negative")

    @property
    def available(self) -> int:
        """Stock that can still be promised to customers."""
        return max(self.on_hand - self.reserved, 0)

    @property
    def stock_value(self) -> Decimal:
        return round_cents(self.unit_cost * self.on_hand)
