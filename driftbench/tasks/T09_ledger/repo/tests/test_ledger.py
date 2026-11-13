from datetime import date
from decimal import Decimal

import pytest

from ledger import AccountFrozen, InsufficientFunds, Ledger, UnknownAccount


def test_deposit_and_balance(book):
    book.deposit("ALICE", "20.50", date(2024, 1, 2), memo="gift")
    assert book.balance("ALICE") == Decimal("120.50")
    assert book.transactions[-1].memo == "gift"


def test_withdraw(book):
    tx = book.withdraw("ALICE", "40", date(2024, 1, 3))
    assert tx.amount == -4000
    assert book.balance("ALICE") == Decimal("60.00")


def test_withdraw_more_than_balance(book):
    with pytest.raises(InsufficientFunds):
        book.withdraw("ALICE", "100.01", date(2024, 1, 3))
    assert book.balance("ALICE") == Decimal("100.00")


def test_available_includes_overdraft(book):
    assert book.available("BOB") == Decimal("50.00")
    assert book.available("ALICE") == Decimal("100.00")


def test_frozen_account(book):
    book.freeze("ALICE")
    with pytest.raises(AccountFrozen):
        book.deposit("ALICE", "1", date(2024, 1, 3))
    book.unfreeze("ALICE")
    book.deposit("ALICE", "1", date(2024, 1, 3))


def test_unknown_account(book):
    with pytest.raises(UnknownAccount):
        book.balance("CAROL")


def test_amount_must_be_positive(book):
    for bad in ["0", "-5"]:
        with pytest.raises(ValueError):
            book.deposit("ALICE", bad, date(2024, 1, 3))


def test_duplicate_account():
    led = Ledger()
    led.open_account("ALICE", "Alice")
    with pytest.raises(ValueError):
        led.open_account("ALICE", "Alice again")
