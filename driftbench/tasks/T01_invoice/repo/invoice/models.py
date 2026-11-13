"""Data model for invoices."""
from dataclasses import dataclass, field
from decimal import Decimal
from typing import List


@dataclass
class LineItem:
    sku: str
    description: str
    quantity: int
    unit_price: Decimal

    def total(self) -> Decimal:
        return self.unit_price * self.quantity


@dataclass
class Invoice:
    number: str
    customer: str
    items: List[LineItem] = field(default_factory=list)

    def add(self, item: LineItem) -> None:
        if item.quantity <= 0:
            raise ValueError("quantity must be positive")
        self.items.append(item)

    def __len__(self) -> int:
        return len(self.items)
