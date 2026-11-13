import pytest

from units import IncompatibleUnits, UnknownUnit, convert
from units.dimensions import LENGTH


def test_convert_length():
    assert convert(5, "km", "m") == 5000.0
    assert convert(12, "in", "ft") == pytest.approx(1.0)


def test_convert_mass_and_time():
    assert convert(2, "lb", "kg") == pytest.approx(0.90718474)
    assert convert(90, "min", "h") == 1.5


def test_incompatible():
    with pytest.raises(IncompatibleUnits):
        convert(1, "kg", "m")


def test_unknown():
    with pytest.raises(UnknownUnit, match="parsec"):
        convert(1, "parsec", "m")


def test_define_custom_unit(reg):
    reg.define("furlong", LENGTH, 201.168)
    assert reg.convert(1, "furlong", "m") == pytest.approx(201.168)
    with pytest.raises(ValueError):
        reg.define("furlong", LENGTH, 1)


def test_symbols(reg):
    assert {"m", "km", "kg", "s", "h"} <= set(reg.symbols())
    assert "km" in reg and "parsec" not in reg
