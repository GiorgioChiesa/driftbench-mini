from decimal import Decimal
from invoice import Invoice, LineItem
from invoice.report import render_text


def test_u1_item_count_line():
    inv = Invoice("S", "Cust")
    inv.add(LineItem("a", "a", 1, Decimal("1")))
    inv.add(LineItem("b", "b", 1, Decimal("1")))
    lines = render_text(inv).splitlines()
    i = next(n for n, l in enumerate(lines) if l.startswith("Customer:"))
    assert lines[i + 1].strip() == "Items: 2"
