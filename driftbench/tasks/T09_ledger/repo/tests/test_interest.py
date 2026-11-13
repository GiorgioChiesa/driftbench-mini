from datetime import date
from decimal import Decimal

import pytest

from ledger.interest import days_between, interest_for_period, simple_interest


def test_days_between():
    assert days_between(date(2024, 1, 1), date(2024, 3, 1)) == 60
    with pytest.raises(ValueError):
        days_between(date(2024, 3, 1), date(2024, 1, 1))


def test_simple_interest():
    assert simple_interest(Decimal("1000.00"), Decimal("0.05"), 365) == Decimal("50.00")
    assert simple_interest(Decimal("1000.00"), Decimal("0.05"), 30) == Decimal("4.11")


def test_interest_for_period():
    assert interest_for_period(Decimal("365.00"), Decimal("0.10"), date(2024, 1, 1), date(2024, 1, 11)) == Decimal("1.00")
