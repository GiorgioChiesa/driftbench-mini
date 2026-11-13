"""Unit registry and conversions between units of the same dimension."""
from __future__ import annotations

import re
from dataclasses import dataclass

from .catalog import CATALOG
from .dimensions import TEMPERATURE, Dimension

# kelvin is the SI unit; value_in_K = value * factor + offset
TEMPERATURE_UNITS = {
    "K": (1.0, 0.0),
    "C": (1.0, 273.15),
    "F": (5.0 / 9.0, 273.15 - 32.0 * 5.0 / 9.0),
}

_QUANTITY = re.compile(r"^\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)\s*([^\s\d.+-]\S*)\s*$")


class UnknownUnit(ValueError):
    """Raised when a unit symbol is not defined in the registry."""

    def __init__(self, symbol: str) -> None:
        super().__init__(f"unknown unit {symbol!r}")
        self.symbol = symbol


class IncompatibleUnits(ValueError):
    """Raised when converting between units of different dimensions."""


@dataclass(frozen=True)
class Unit:
    """A unit: ``value_in_si = value * factor + offset``."""

    symbol: str
    dimension: Dimension
    factor: float
    offset: float = 0.0

    def to_si(self, value: float) -> float:
        return value * self.factor + self.offset

    def from_si(self, value: float) -> float:
        return (value - self.offset) / self.factor


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
        for symbol, (factor, offset) in TEMPERATURE_UNITS.items():
            reg.define(symbol, TEMPERATURE, factor, offset)
        return reg

    def define(self, symbol: str, dimension: Dimension, factor: float, offset: float = 0.0) -> Unit:
        if symbol in self._units:
            raise ValueError(f"unit {symbol!r} is already defined")
        if factor <= 0:
            raise ValueError("factor must be positive")
        unit = Unit(symbol, dimension, float(factor), float(offset))
        self._units[symbol] = unit
        return unit

    def get(self, symbol: str) -> Unit:
        unit = self._units.get(symbol)
        if unit is not None:
            return unit
        if "/" in symbol:
            num, _, den = symbol.rpartition("/")
            a, b = self.get(num), self.get(den)
            if a.offset or b.offset:
                raise IncompatibleUnits(f"offset unit cannot be part of a compound unit: {symbol}")
            return Unit(symbol, a.dimension / b.dimension, a.factor / b.factor)
        raise UnknownUnit(symbol)

    def __contains__(self, symbol: object) -> bool:
        return symbol in self._units

    def symbols(self) -> list[str]:
        return sorted(self._units)

    def convert(self, value: float, src: str, dst: str) -> float:
        a, b = self.get(src), self.get(dst)
        if a.dimension != b.dimension:
            raise IncompatibleUnits(f"cannot convert {src} ({a.dimension}) to {dst} ({b.dimension})")
        return b.from_si(a.to_si(value))

    def parse(self, text: str):
        """Parse ``"3.5 km"`` into ``Quantity(3.5, "km")``."""
        from .quantity import Quantity

        match = _QUANTITY.match(text)
        if not match:
            raise ValueError(f"cannot parse quantity: {text!r}")
        value, symbol = match.groups()
        self.get(symbol)
        return Quantity(float(value), symbol)


DEFAULT = Registry.with_defaults()


def convert(value: float, src: str, dst: str) -> float:
    """Convert ``value`` from ``src`` to ``dst`` with the default registry."""
    return DEFAULT.convert(value, src, dst)


def parse(text: str):
    """Parse a quantity such as ``"3.5 km"`` with the default registry."""
    return DEFAULT.parse(text)
