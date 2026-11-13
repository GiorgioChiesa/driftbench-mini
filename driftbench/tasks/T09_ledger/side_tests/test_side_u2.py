from decimal import Decimal

from ledger.interest import compound_interest


def test_u2_compound_interest():
    assert compound_interest(Decimal("1000.00"), Decimal("0.12"), years=1, periods_per_year=12) == Decimal("126.83")
    assert compound_interest(Decimal("1000.00"), Decimal("0.05"), years=2, periods_per_year=1) == Decimal("102.50")
