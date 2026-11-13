"""Transaction records and the append-only journal."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from itertools import count
from typing import Iterator

KINDS = ("deposit", "withdrawal", "transfer_in", "transfer_out", "interest", "fee")


@dataclass(frozen=True)
class Transaction:
    """One journal entry. ``amount`` is in cents: credits are positive, debits negative."""

    seq: int
    account: str
    when: date
    kind: str
    amount: int
    memo: str = ""


class Journal:
    """Append-only list of transactions, numbered in recording order."""

    def __init__(self) -> None:
        self._items: list[Transaction] = []
        self._seq = count(1)

    def record(self, account: str, when: date, kind: str, amount: int, memo: str = "") -> Transaction:
        if kind not in KINDS:
            raise ValueError(f"unknown transaction kind {kind!r}")
        tx = Transaction(next(self._seq), account, when, kind, amount, memo)
        self._items.append(tx)
        return tx

    def __iter__(self) -> Iterator[Transaction]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def for_account(self, account: str) -> list[Transaction]:
        """All transactions of ``account``, in recording order."""
        return [tx for tx in self._items if tx.account == account]

    def between(self, account: str, start: date, end: date) -> list[Transaction]:
        """Transactions of ``account`` dated ``start``..``end`` (inclusive), oldest first.

        Transactions with the same date keep their recording order.
        """
        rows = [tx for tx in self.for_account(account) if start <= tx.when <= end]
        return sorted(rows, key=lambda tx: (tx.when, tx.seq))
