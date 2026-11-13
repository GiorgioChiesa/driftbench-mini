from datetime import date
from decimal import Decimal

from ledger import Ledger
from ledger.export import summary


def test_u3_summary_by_kind():
    book = Ledger()
    book.open_account("ALICE", "Alice")
    book.deposit("ALICE", "5.00", date(2024, 1, 1))
    book.deposit("ALICE", "2.50", date(2024, 1, 2))
    book.withdraw("ALICE", "1.00", date(2024, 1, 3))
    assert summary(book.transactions) == {"deposit": Decimal("7.50"), "withdrawal": Decimal("-1.00")}
