import csv
from decimal import Decimal


def make_items():
    from inventory import Item

    return [
        Item("B-200", "Hex bolt", "Acme", on_hand=150, reserved=10, unit_cost="0.08", reorder_point=200, reorder_qty=0),
        Item("A-100", "Anchor", "Acme", on_hand=30, reserved=0, unit_cost="0.125", reorder_point=40, reorder_qty=25),
        Item("W-110", "Washer", "", on_hand=0, reserved=0, unit_cost="0.02", reorder_point=100, reorder_qty=500),
        Item("C-300", "Clamp", "Bolton", on_hand=60, reserved=10, unit_cost="2.50", reorder_point=50, reorder_qty=10),
        Item("G-900", "Glue", "Bolton", on_hand=500, reserved=0, unit_cost="3.75", reorder_point=50, reorder_qty=0),
        Item("T-400", "Tape", "Zeta", on_hand=0, reserved=0, unit_cost="1.00", reorder_point=0, reorder_qty=5),
    ]


def test_r1_needs_reorder():
    from inventory import Item, reports

    by_sku = {item.sku: item for item in make_items()}
    assert reports.needs_reorder(by_sku["B-200"]) is True     # available 140 <= 200
    assert reports.needs_reorder(by_sku["C-300"]) is True     # available 50 == 50 (reserved counts)
    assert reports.needs_reorder(by_sku["G-900"]) is False
    assert reports.needs_reorder(by_sku["T-400"]) is False    # no reorder point
    assert reports.needs_reorder(Item("X-100", "x", on_hand=12, reorder_point=10, reorder_qty=50)) is False


def test_r2_order_quantity():
    from inventory import reports

    by_sku = {item.sku: item for item in make_items()}
    assert reports.order_quantity(by_sku["B-200"]) == 260     # 400 - 140, no pack size
    assert reports.order_quantity(by_sku["A-100"]) == 50      # 80 - 30 = 50, multiple of 25
    assert reports.order_quantity(by_sku["W-110"]) == 500     # 200 rounded up to 500
    assert reports.order_quantity(by_sku["C-300"]) == 50      # 100 - 50 = 50
    assert reports.order_quantity(by_sku["G-900"]) == 0


def test_r3_reorder_report():
    from inventory import reports

    lines = reports.reorder_report(make_items())
    assert [(l.supplier, l.sku) for l in lines] == [("", "W-110"), ("Acme", "A-100"), ("Acme", "B-200"), ("Bolton", "C-300")]
    a = lines[1]
    assert a._fields == ("supplier", "sku", "name", "available", "order_qty", "cost")
    assert (a.name, a.available, a.order_qty) == ("Anchor", 30, 50)
    assert a.cost == Decimal("6.25")
    assert lines[2].cost == Decimal("20.80")
    assert lines[0].cost == Decimal("10.00")


def test_r3_cost_rounding_half_up():
    from inventory import Item, reports

    (line,) = reports.reorder_report([Item("R-100", "r", "S", on_hand=0, unit_cost="0.125", reorder_point=1)])
    assert line.order_qty == 2 and line.cost == Decimal("0.25")
    (line,) = reports.reorder_report([Item("R-101", "r", "S", on_hand=0, unit_cost="0.0125", reorder_point=1, reorder_qty=2)])
    assert line.cost == Decimal("0.03")


def test_r4_group_by_supplier():
    from inventory import reports

    groups = reports.group_by_supplier(reports.reorder_report(make_items()))
    assert list(groups) == ["Acme", "Bolton", "UNASSIGNED"]
    assert [l.sku for l in groups["Acme"]] == ["A-100", "B-200"]
    assert [l.sku for l in groups["UNASSIGNED"]] == ["W-110"]


def test_r5_supplier_totals():
    from inventory import reports

    totals = reports.supplier_totals(reports.reorder_report(make_items()))
    assert totals == {"Acme": Decimal("27.05"), "Bolton": Decimal("125.00"), "UNASSIGNED": Decimal("10.00")}
    assert list(totals) == ["Acme", "Bolton", "UNASSIGNED"]


def test_r6_export_reorder_csv(tmp_path):
    from inventory import reports

    lines = reports.reorder_report(make_items())
    path = tmp_path / "reorder.csv"
    assert reports.export_reorder_csv(lines, path) == 4
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    assert rows[0] == ["supplier", "sku", "name", "available", "order_qty", "cost"]
    assert rows[1] == ["", "W-110", "Washer", "0", "500", "10.00"]
    assert rows[2] == ["Acme", "A-100", "Anchor", "30", "50", "6.25"]
    assert len(rows) == 5
