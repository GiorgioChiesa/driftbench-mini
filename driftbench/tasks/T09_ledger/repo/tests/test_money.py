from decimal import Decimal

import pytest

from ledger.money import fmt, from_cents, to_cents


def test_to_cents():
    assert to_cents("12.34") == 1234
    assert to_cents(Decimal("0.005")) == 1
    assert to_cents(7) == 700
    assert to_cents(" -3.5 ") == -350


def test_to_cents_rejects():
    with pytest.raises(TypeError):
        to_cents(1.5)
    for bad in ["abc", "", "NaN"]:
        with pytest.raises(ValueError):
            to_cents(bad)


def test_from_cents():
    assert from_cents(1234) == Decimal("12.34")
    assert from_cents(-5) == Decimal("-0.05")
    assert str(from_cents(-1250)) == "-12.50"


def test_fmt():
    assert fmt(123450) == "1,234.50 EUR"
    assert fmt(-99, "USD") == "-0.99 USD"
