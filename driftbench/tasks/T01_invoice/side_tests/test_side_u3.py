from decimal import Decimal
from invoice import Invoice, LineItem


def test_u3_repr():
    inv = Invoice("2024-007", "Cust")
    inv.add(LineItem("a", "a", 1, Decimal("1")))
    inv.add(LineItem("b", "b", 1, Decimal("1")))
    assert repr(inv) == "Invoice(number='2024-007', items=2)"
