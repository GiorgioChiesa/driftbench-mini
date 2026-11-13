import pytest

from units import Quantity
from units.dimensions import LENGTH


def test_to():
    assert Quantity(90, "min").to("h") == Quantity(1.5, "h")


def test_to_with_custom_registry(reg):
    reg.define("furlong", LENGTH, 201.168)
    assert Quantity(2, "furlong").to("m", reg).value == pytest.approx(402.336)


def test_arithmetic():
    assert Quantity(1, "m") + Quantity(2, "m") == Quantity(3, "m")
    assert Quantity(5, "s") - Quantity(2, "s") == Quantity(3, "s")
    assert -Quantity(1, "kg") == Quantity(-1, "kg")


def test_unit_mismatch():
    with pytest.raises(ValueError):
        Quantity(1, "m") + Quantity(1, "km")


def test_str():
    assert str(Quantity(3.5, "km")) == "3.5 km"
