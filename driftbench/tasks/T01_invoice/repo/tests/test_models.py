from decimal import Decimal

import pytest

from invoice import Invoice, LineItem


def test_line_total():
    assert LineItem("x", "x", 3, Decimal("2.50")).total() == Decimal("7.50")


def test_add_rejects_zero_quantity():
    with pytest.raises(ValueError):
        Invoice("1", "c").add(LineItem("x", "x", 0, Decimal("1")))


def test_len(sample):
    assert len(sample) == 2
