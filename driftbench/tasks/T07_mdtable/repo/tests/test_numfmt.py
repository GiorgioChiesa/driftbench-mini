from decimal import Decimal

import pytest

from mdtable.numfmt import format_number, is_number, percent


def test_is_number():
    assert is_number(1) and is_number(1.5) and is_number(Decimal("2"))
    assert not is_number(True) and not is_number("3")


def test_plain():
    assert format_number(1234) == "1234"
    assert format_number(0.1) == "0.1"
    assert format_number(1e20) == "100000000000000000000"


def test_decimals_round_half_up():
    assert format_number(2.5, 0) == "3"
    assert format_number(1.005, 2) == "1.01"
    assert format_number(7, 2) == "7.00"


def test_thousands():
    assert format_number(-1234567.891, 2, thousands=",") == "-1,234,567.89"


def test_percent():
    assert percent(0.125) == "12.5%"


def test_rejects_non_numbers():
    with pytest.raises(TypeError):
        format_number("12")
    with pytest.raises(ValueError):
        format_number(1, -1)
