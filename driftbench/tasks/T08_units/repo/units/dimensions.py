"""Physical dimensions as products of integer powers of base quantities."""
from __future__ import annotations

BASE_QUANTITIES = ("length", "mass", "time", "temperature")


class Dimension:
    """An immutable mapping base quantity -> exponent, e.g. velocity is length**1 * time**-1."""

    __slots__ = ("_exps",)

    def __init__(self, **exponents: int) -> None:
        unknown = set(exponents) - set(BASE_QUANTITIES)
        if unknown:
            raise ValueError(f"unknown base quantities: {sorted(unknown)}")
        self._exps = tuple(sorted((k, int(v)) for k, v in exponents.items() if v))

    def exponent(self, base: str) -> int:
        return dict(self._exps).get(base, 0)

    @property
    def is_dimensionless(self) -> bool:
        return not self._exps

    def __mul__(self, other: "Dimension") -> "Dimension":
        exps = dict(self._exps)
        for k, v in other._exps:
            exps[k] = exps.get(k, 0) + v
        return Dimension(**exps)

    def __truediv__(self, other: "Dimension") -> "Dimension":
        exps = dict(self._exps)
        for k, v in other._exps:
            exps[k] = exps.get(k, 0) - v
        return Dimension(**exps)

    def __pow__(self, n: int) -> "Dimension":
        return Dimension(**{k: v * n for k, v in self._exps})

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Dimension) and self._exps == other._exps

    def __hash__(self) -> int:
        return hash(self._exps)

    def __repr__(self) -> str:
        inner = ", ".join(f"{k}={v}" for k, v in self._exps)
        return f"Dimension({inner})"


DIMENSIONLESS = Dimension()
LENGTH = Dimension(length=1)
MASS = Dimension(mass=1)
TIME = Dimension(time=1)
TEMPERATURE = Dimension(temperature=1)
AREA = LENGTH ** 2
VELOCITY = LENGTH / TIME
