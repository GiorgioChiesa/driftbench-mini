"""Quantities: a numeric value together with its unit symbol."""
from __future__ import annotations

from dataclasses import dataclass

from . import registry as _registry


@dataclass(frozen=True)
class Quantity:
    value: float
    unit: str

    def to(self, unit: str, registry: "_registry.Registry | None" = None) -> "Quantity":
        """Return the same quantity expressed in ``unit``."""
        reg = registry or _registry.DEFAULT
        return Quantity(reg.convert(self.value, self.unit, unit), unit)

    def _same_unit(self, other: "Quantity") -> None:
        if other.unit != self.unit:
            raise ValueError(f"unit mismatch: {self.unit} vs {other.unit}; convert first")

    def __add__(self, other: object) -> "Quantity":
        if not isinstance(other, Quantity):
            return NotImplemented
        self._same_unit(other)
        return Quantity(self.value + other.value, self.unit)

    def __sub__(self, other: object) -> "Quantity":
        if not isinstance(other, Quantity):
            return NotImplemented
        self._same_unit(other)
        return Quantity(self.value - other.value, self.unit)

    def __neg__(self) -> "Quantity":
        return Quantity(-self.value, self.unit)

    def __str__(self) -> str:
        return f"{self.value:g} {self.unit}"
