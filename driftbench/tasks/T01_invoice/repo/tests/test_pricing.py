from decimal import Decimal

import pytest

from invoice import pricing


def test_subtotal(sample):
    assert pricing.subtotal(sample) == Decimal("33.50")


def test_apply_tax():
    assert pricing.apply_tax(Decimal("100.00"), Decimal("0.22")) == Decimal("122.00")


def test_negative_rate():
    with pytest.raises(ValueError):
        pricing.apply_tax(Decimal("1"), Decimal("-0.1"))
