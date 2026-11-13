"""The ledger: a set of accounts plus the journal of their transactions."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from .accounts import Account
from .money import from_cents, to_cents
from .transactions import Journal, Transaction


class LedgerError(Exception):
    """Base class for ledger errors."""


class UnknownAccount(LedgerError):
    pass


class AccountFrozen(LedgerError):
    pass


class InsufficientFunds(LedgerError):
    pass


@dataclass(frozen=True)
class StatementLine:
    when: date
    kind: str
    memo: str
    amount: Decimal
    balance: Decimal


class Ledger:
    def __init__(self) -> None:
        self.accounts: dict[str, Account] = {}
        self.journal = Journal()

    def open_account(self, account_id: str, owner: str, overdraft_limit: Decimal | str = "0") -> Account:
        if account_id in self.accounts:
            raise ValueError(f"account {account_id!r} already exists")
        account = Account(account_id, owner, overdraft_limit=to_cents(overdraft_limit))
        self.accounts[account_id] = account
        return account

    def account(self, account_id: str) -> Account:
        try:
            return self.accounts[account_id]
        except KeyError:
            raise UnknownAccount(account_id) from None

    def freeze(self, account_id: str) -> None:
        self.account(account_id).frozen = True

    def unfreeze(self, account_id: str) -> None:
        self.account(account_id).frozen = False

    def balance(self, account_id: str) -> Decimal:
        return from_cents(self.account(account_id).balance)

    def available(self, account_id: str) -> Decimal:
        """Money that can still be taken out, overdraft included."""
        return from_cents(self.account(account_id).headroom())

    @property
    def transactions(self) -> list[Transaction]:
        return list(self.journal)

    def deposit(self, account_id: str, amount: Decimal | str, when: date, memo: str = "") -> Transaction:
        account = self._active(account_id)
        cents = self._positive(amount)
        account.balance += cents
        return self.journal.record(account.id, when, "deposit", cents, memo)

    def withdraw(self, account_id: str, amount: Decimal | str, when: date, memo: str = "") -> Transaction:
        """Take money out; the balance may go down to minus the overdraft limit."""
        account = self._active(account_id)
        cents = self._positive(amount)
        self._check_funds(account, cents)
        account.balance -= cents
        return self.journal.record(account.id, when, "withdrawal", -cents, memo)

    def transfer(
        self, src: str, dst: str, amount: Decimal | str, when: date, memo: str = ""
    ) -> tuple[Transaction, Transaction]:
        """Move money between two accounts. Everything is validated before anything changes."""
        cents = self._positive(amount)
        source, target = self.account(src), self.account(dst)
        if source.id == target.id:
            raise ValueError("cannot transfer to the same account")
        for account in (source, target):
            if account.frozen:
                raise AccountFrozen(account.id)
        self._check_funds(source, cents)
        source.balance -= cents
        target.balance += cents
        out_tx = self.journal.record(source.id, when, "transfer_out", -cents, memo)
        in_tx = self.journal.record(target.id, when, "transfer_in", cents, memo)
        return out_tx, in_tx

    def statement(self, account_id: str, start: date, end: date) -> list[StatementLine]:
        """Transactions dated start..end (inclusive) with a running balance."""
        account = self.account(account_id)
        if start > end:
            raise ValueError("start must not be after end")
        running = sum(tx.amount for tx in self.journal.for_account(account.id) if tx.when < start)
        lines = []
        for tx in self.journal.between(account.id, start, end):
            running += tx.amount
            lines.append(StatementLine(tx.when, tx.kind, tx.memo, from_cents(tx.amount), from_cents(running)))
        return lines

    @staticmethod
    def _check_funds(account: Account, cents: int) -> None:
        if account.balance - cents < account.floor:
            raise InsufficientFunds(
                f"{account.id}: {from_cents(cents)} exceeds available {from_cents(account.headroom())}"
            )

    def _active(self, account_id: str) -> Account:
        account = self.account(account_id)
        if account.frozen:
            raise AccountFrozen(account_id)
        return account

    @staticmethod
    def _positive(amount: Decimal | str) -> int:
        cents = to_cents(amount)
        if cents <= 0:
            raise ValueError("amount must be positive")
        return cents
