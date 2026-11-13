import pytest

from inventory import Ledger


def test_receive_and_ship(items):
    ledger = Ledger(items)
    ledger.receive("W-110", 300)
    ledger.ship("W-110", 120, note="order 77")
    assert ledger.item("W-110").on_hand == 180
    assert [(m.kind, m.quantity) for m in ledger.history("W-110")] == [("receive", 300), ("ship", 120)]


def test_ship_respects_reservations(items):
    ledger = Ledger(items)
    with pytest.raises(ValueError):
        ledger.ship("G-900", 12)


def test_reserve_and_release(items):
    ledger = Ledger(items)
    ledger.reserve("N-310", 20)
    ledger.release("N-310", 50)
    assert ledger.item("N-310").reserved == 0
    assert len(ledger.history()) == 2


def test_invalid_quantity(items):
    with pytest.raises(ValueError):
        Ledger(items).receive("B-200", 0)


def test_unknown_sku(items):
    with pytest.raises(KeyError):
        Ledger(items).receive("Z-999", 1)
