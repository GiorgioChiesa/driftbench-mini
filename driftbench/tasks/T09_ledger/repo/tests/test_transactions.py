from datetime import date

import pytest

from ledger import Journal


def test_record_numbers_entries():
    j = Journal()
    a = j.record("A1", date(2024, 1, 1), "deposit", 100)
    b = j.record("A1", date(2024, 1, 2), "withdrawal", -50, memo="atm")
    assert (a.seq, b.seq) == (1, 2)
    assert len(j) == 2
    assert b.memo == "atm"


def test_unknown_kind():
    with pytest.raises(ValueError):
        Journal().record("A1", date(2024, 1, 1), "gift", 1)


def test_between_is_inclusive_and_sorted():
    j = Journal()
    j.record("A1", date(2024, 1, 31), "deposit", 1)
    j.record("A1", date(2024, 1, 1), "deposit", 2)
    j.record("B2", date(2024, 1, 15), "deposit", 3)
    j.record("A1", date(2024, 1, 1), "fee", -4)
    j.record("A1", date(2024, 2, 1), "deposit", 5)
    rows = j.between("A1", date(2024, 1, 1), date(2024, 1, 31))
    assert [tx.amount for tx in rows] == [2, -4, 1]
