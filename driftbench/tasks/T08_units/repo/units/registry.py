"""Unit registry and conversions between units of the same dimension."""
from __future__ import annotations

from dataclasses import dataclass

from .catalog import CATALOG
from .dimensions import Dimension


class UnknownUnit(ValueError):
    """Raised when a unit symbol is not defined in the registry."""

    def __init__(self, symbol: str) -> None:
        super().__init__(f"unknown unit {symbol!r}")
        self.symbol = symbol


class IncompatibleUnits(ValueError):
    """Raised when converting between units of different dimensions."""


@dataclass(frozen=True)
class Unit:
    """A unit: ``value_in_si = value * factor``."""

    symbol: str
    dimension: Dimension
    factor: float

    def to_si(self, value: float) -> float:
        return value * self.factor

    def from_si(self, value: float) -> float:
        return value / self.factor


class Registry:
    """A set of named units. Use :meth:`with_defaults` for the built-in catalog."""

    def __init__(self) -> None:
        self._units: dict[str, Unit] = {}

    @classmethod
    def with_defaults(cls) -> "Registry":
        reg = cls()
        for dimension, table in CATALOG:
            for symbol, factor in table.items():
                reg.define(symbol, dimension, factor)
        return reg

    def define(self, symbol: str, dimension: Dimension, factor: float) -> Unit:
        if symbol in self._units:
            raise ValueError(f"unit {symbol!r} is already defined")
        if factor <= 0:
            raise ValueError("factor must be positive")
        unit = Unit(symbol, dimension, float(factor))
        self._units[symbol] = unit
        return unit

    def get(self, symbol: str) -> Unit:
        try:
            return self._units[symbol]
        except KeyError:
            raise UnknownUnit(symbol) from None

    def __contains__(self, symbol: object) -> bool:
        return symbol in self._units

    def symbols(self) -> list[str]:
        return sorted(self._units)

    def convert(self, value: float, src: str, dst: str) -> float:
        a, b = self.get(src), self.get(dst)
        if a.dimension != b.dimension:
            raise IncompatibleUnits(f"cannot convert {src} ({a.dimension}) to {dst} ({b.dimension})")
        return b.from_si(a.to_si(value))


DEFAULT = Registry.with_defaults()


def convert(value: float, src: str, dst: str) -> float:
    """Convert ``value`` from ``src`` to ``dst`` with the default registry."""
    return DEFAULT.convert(value, src, dst)
