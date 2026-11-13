from datetime import date

from ledger import Ledger
from ledger.export import to_csv


def test_u1_csv_delimiter():
    book = Ledger()
    book.open_account("ALICE", "Alice")
    book.deposit("ALICE", "5.00", date(2024, 1, 1))
    lines = to_csv(book.transactions, delimiter=";").splitlines()
    assert lines == ["seq;account;date;kind;amount", "1;ALICE;2024-01-01;deposit;5.00"]
