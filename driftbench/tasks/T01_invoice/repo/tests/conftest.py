from decimal import Decimal

import pytest

from invoice import Invoice, LineItem


@pytest.fixture
def sample():
    inv = Invoice("2024-007", "ACME S.p.A.")
    inv.add(LineItem("A1", "Widget", 2, Decimal("10.00")))
    inv.add(LineItem("B2", "Gadget", 3, Decimal("4.50")))
    return inv
