"""Export journal entries to CSV or JSON."""
from __future__ import annotations

import csv
import io
import json
from typing import Iterable

from .money import from_cents
from .transactions import Transaction

CSV_FIELDS = ["seq", "account", "date", "kind", "amount"]


def _row(tx: Transaction) -> list:
    return [tx.seq, tx.account, tx.when.isoformat(), tx.kind, str(from_cents(tx.amount))]


def to_csv(transactions: Iterable[Transaction]) -> str:
    """CSV text with a header row; amounts as plain decimals (``-20.00``)."""
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(CSV_FIELDS)
    for tx in transactions:
        writer.writerow(_row(tx))
    return buf.getvalue()


def to_json(transactions: Iterable[Transaction]) -> str:
    """JSON array of objects; amounts are strings to avoid float rounding."""
    items = [
        {"seq": tx.seq, "account": tx.account, "date": tx.when.isoformat(), "kind": tx.kind,
         "amount": str(from_cents(tx.amount)), "memo": tx.memo}
        for tx in transactions
    ]
    return json.dumps(items, indent=2)
