from datetime import date
from decimal import Decimal

import pytest

D1 = date(2024, 3, 1)


def make():
    from ledger.ledger import Ledger

    book = Ledger()
    book.open_account("ALICE", "Alice")
    book.open_account("BOB", "Bob")
    book.open_account("CAROL", "Carol", overdraft_limit="50.00")
    book.deposit("ALICE", "100.00", D1)
    return book


def test_r1_transfer_moves_money():
    book = make()
    out_tx, in_tx = book.transfer("ALICE", "BOB", "30.00", date(2024, 3, 2), memo="rent")
    assert book.balance("ALICE") == Decimal("70.00")
    assert book.balance("BOB") == Decimal("30.00")
    assert (out_tx.account, out_tx.kind, out_tx.amount, out_tx.memo) == ("ALICE", "transfer_out", -3000, "rent")
    assert (in_tx.account, in_tx.kind, in_tx.amount, in_tx.memo) == ("BOB", "transfer_in", 3000, "rent")
    assert out_tx.when == in_tx.when == date(2024, 3, 2)
    assert book.transactions[-2:] == [out_tx, in_tx]
    book.transfer("BOB", "ALICE", Decimal("0.01"), D1)
    assert book.balance("BOB") == Decimal("29.99")


def test_r2_transfer_validation():
    from ledger.ledger import AccountFrozen, UnknownAccount

    book = make()
    for bad in ["0", "-1.00"]:
        with pytest.raises(ValueError):
            book.transfer("ALICE", "BOB", bad, D1)
    with pytest.raises(UnknownAccount):
        book.transfer("ALICE", "NOBODY", "1.00", D1)
    with pytest.raises(UnknownAccount):
        book.transfer("NOBODY", "ALICE", "1.00", D1)
    with pytest.raises(ValueError):
        book.transfer("ALICE", "ALICE", "1.00", D1)
    book.freeze("ALICE")
    with pytest.raises(AccountFrozen):
        book.transfer("ALICE", "BOB", "1.00", D1)
    book.unfreeze("ALICE")
    book.freeze("BOB")
    with pytest.raises(AccountFrozen):
        book.transfer("ALICE", "BOB", "1.00", D1)


def test_r3_overdraft_rules():
    from ledger.ledger import InsufficientFunds

    book = make()
    book.deposit("CAROL", "20.00", D1)
    book.withdraw("CAROL", "60.00", D1)
    assert book.balance("CAROL") == Decimal("-40.00")
    book.transfer("CAROL", "BOB", "10.00", D1)
    assert book.balance("CAROL") == Decimal("-50.00")
    with pytest.raises(InsufficientFunds):
        book.withdraw("CAROL", "0.01", D1)
    with pytest.raises(InsufficientFunds):
        book.transfer("CAROL", "BOB", "0.01", D1)
    with pytest.raises(InsufficientFunds):
        book.transfer("BOB", "ALICE", "10.01", D1)
    with pytest.raises(InsufficientFunds):
        book.withdraw("ALICE", "100.01", D1)
    book.transfer("ALICE", "BOB", "100.00", D1)
    assert book.balance("ALICE") == Decimal("0.00")


def test_r4_transfer_is_atomic():
    from ledger.ledger import AccountFrozen, InsufficientFunds, UnknownAccount

    book = make()
    before = (book.balance("ALICE"), book.balance("BOB"), len(book.transactions))
    book.freeze("BOB")
    with pytest.raises(AccountFrozen):
        book.transfer("ALICE", "BOB", "10.00", D1)
    book.unfreeze("BOB")
    with pytest.raises(UnknownAccount):
        book.transfer("ALICE", "NOBODY", "10.00", D1)
    with pytest.raises(InsufficientFunds):
        book.transfer("ALICE", "BOB", "500.00", D1)
    with pytest.raises(ValueError):
        book.transfer("ALICE", "BOB", "ten", D1)
    assert (book.balance("ALICE"), book.balance("BOB"), len(book.transactions)) == before


def test_r5_statement_running_balance():
    book = make()
    book.deposit("ALICE", "100.00", date(2024, 1, 5), memo="salary")
    book.withdraw("ALICE", "20.00", date(2024, 1, 10), memo="atm")
    book.transfer("ALICE", "BOB", "30.00", date(2024, 2, 1), memo="rent")
    book.deposit("ALICE", "5.00", date(2024, 2, 1), memo="refund")
    book.deposit("ALICE", "10.00", date(2024, 1, 20), memo="late entry")
    book.withdraw("ALICE", "1.00", date(2024, 2, 15), memo="fee")
    lines = book.statement("ALICE", date(2024, 1, 10), date(2024, 2, 1))
    assert [(l.when, l.kind, l.memo, l.amount, l.balance) for l in lines] == [
        (date(2024, 1, 10), "withdrawal", "atm", Decimal("-20.00"), Decimal("80.00")),
        (date(2024, 1, 20), "deposit", "late entry", Decimal("10.00"), Decimal("90.00")),
        (date(2024, 2, 1), "transfer_out", "rent", Decimal("-30.00"), Decimal("60.00")),
        (date(2024, 2, 1), "deposit", "refund", Decimal("5.00"), Decimal("65.00")),
    ]
    assert all(isinstance(l.amount, Decimal) and isinstance(l.balance, Decimal) for l in lines)
    bob = book.statement("BOB", date(2024, 1, 1), date(2024, 12, 31))
    assert [(l.kind, l.balance) for l in bob] == [("transfer_in", Decimal("30.00"))]


def test_r6_statement_errors_and_empty():
    from ledger.ledger import UnknownAccount

    book = make()
    with pytest.raises(UnknownAccount):
        book.statement("NOBODY", date(2024, 1, 1), date(2024, 1, 31))
    with pytest.raises(ValueError):
        book.statement("ALICE", date(2024, 2, 1), date(2024, 1, 1))
    assert book.statement("ALICE", date(2023, 1, 1), date(2023, 12, 31)) == []
    assert book.statement("BOB", D1, D1) == []
    assert len(book.statement("ALICE", D1, D1)) == 1
