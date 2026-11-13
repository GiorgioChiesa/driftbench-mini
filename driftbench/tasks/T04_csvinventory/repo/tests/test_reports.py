from decimal import Decimal

from inventory import reports


def test_total_value(items):
    assert reports.total_value(items) == Decimal("98.50")


def test_value_by_supplier(items):
    assert reports.value_by_supplier(items) == {
        "Acme": Decimal("46.00"), "Bolton": Decimal("0.00"), "UNASSIGNED": Decimal("52.50")}


def test_low_stock_uses_available(items):
    assert [item.sku for item in reports.low_stock(items, 150)] == ["W-110", "G-900", "N-310"]


def test_out_of_stock(items):
    assert reports.out_of_stock(items) == ["W-110"]


def test_stock_summary(items):
    assert reports.stock_summary(items) == {"skus": 4, "units": 634, "value": Decimal("98.50"), "out_of_stock": 1}
