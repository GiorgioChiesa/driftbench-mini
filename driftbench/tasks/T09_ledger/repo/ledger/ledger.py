"""The ledger: a set of accounts plus the journal of their transactions."""
from __future__ import annotations

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
        """Take money out. Overdrafts are not supported yet: the balance cannot go below zero."""
        account = self._active(account_id)
        cents = self._positive(amount)
        if account.balance - cents < 0:
            raise InsufficientFunds(
                f"{account_id}: balance {from_cents(account.balance)} is less than {from_cents(cents)}"
            )
        account.balance -= cents
        return self.journal.record(account.id, when, "withdrawal", -cents, memo)

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
