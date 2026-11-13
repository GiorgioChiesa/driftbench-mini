import json
from datetime import date

from ledger.export import to_csv, to_json


def test_to_csv(book):
    book.withdraw("ALICE", "20", date(2024, 1, 2), memo="atm")
    lines = to_csv(book.transactions).splitlines()
    assert lines[0] == "seq,account,date,kind,amount"
    assert lines[2] == "2,ALICE,2024-01-02,withdrawal,-20.00"


def test_to_json(book):
    data = json.loads(to_json(book.transactions))
    assert data == [{"seq": 1, "account": "ALICE", "date": "2024-01-01", "kind": "deposit",
                     "amount": "100.00", "memo": ""}]
