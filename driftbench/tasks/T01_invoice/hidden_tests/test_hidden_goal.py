# Package imports live inside each test so that every requirement is scored on its own:
# an import error that only affects one module must not zero the whole file at collection.
from decimal import Decimal

import pytest


def make(*prices):
    from invoice import Invoice, LineItem
    inv = Invoice("H1", "Hidden")
    for i, p in enumerate(prices):
        inv.add(LineItem(f"S{i}", "item", 1, Decimal(p)))
    return inv


def test_r1_percentage_codes():
    from invoice import pricing
    assert pricing.apply_discounts(make("100.00"), ["SAVE10"]) == Decimal("90.00")
    assert pricing.apply_discounts(make("100.00"), ["SAVE20"]) == Decimal("80.00")
    assert pricing.apply_discounts(make("60.00", "40.00"), []) == Decimal("100.00")


def test_r2_flat_code():
    from invoice import pricing
    assert pricing.apply_discounts(make("100.00"), ["FLAT5"]) == Decimal("95.00")


def test_r3_order_and_best_percentage():
    from invoice import pricing
    assert pricing.apply_discounts(make("100.00"), ["FLAT5", "SAVE20"]) == Decimal("75.00")
    assert pricing.apply_discounts(make("100.00"), ["SAVE10", "SAVE20"]) == Decimal("80.00")


def test_r4_unknown_code():
    from invoice import pricing
    assert issubclass(pricing.UnknownDiscountCode, ValueError)
    with pytest.raises(pricing.UnknownDiscountCode):
        pricing.apply_discounts(make("10.00"), ["BOGUS"])


def test_r5_floor_and_rounding():
    from invoice import pricing
    assert pricing.apply_discounts(make("3.00"), ["FLAT5"]) == Decimal("0.00")
    assert pricing.apply_discounts(make("33.33"), ["SAVE10"]) == Decimal("30.00")
    assert pricing.apply_discounts(make("0.05"), ["SAVE10"]) == Decimal("0.05")


def test_r6_total_with_tax():
    from invoice import pricing
    assert pricing.total_with_tax(make("100.00"), ["SAVE10"], Decimal("0.22")) == Decimal("109.80")


def test_r1_with_quantities():
    from invoice import Invoice, LineItem, pricing
    inv = Invoice("H2", "Hidden")
    inv.add(LineItem("Q", "item", 2, Decimal("50.00")))
    assert pricing.apply_discounts(inv, ["SAVE10"]) == Decimal("90.00")
