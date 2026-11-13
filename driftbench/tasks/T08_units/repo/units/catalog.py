"""Built-in linear units: symbol -> factor to the SI unit of their dimension."""
from __future__ import annotations

from .dimensions import LENGTH, MASS, TIME

LENGTH_UNITS = {
    "m": 1.0,
    "km": 1000.0,
    "cm": 0.01,
    "mm": 0.001,
    "in": 0.0254,
    "ft": 0.3048,
    "mi": 1609.344,     # international mile
}

MASS_UNITS = {
    "kg": 1.0,
    "g": 0.001,
    "t": 1000.0,        # metric tonne
    "lb": 0.45359237,
    "oz": 0.028349523125,
}

TIME_UNITS = {
    "s": 1.0,
    "ms": 0.001,
    "min": 60.0,
    "h": 3600.0,
    "d": 86400.0,
}

CATALOG = [(LENGTH, LENGTH_UNITS), (MASS, MASS_UNITS), (TIME, TIME_UNITS)]
