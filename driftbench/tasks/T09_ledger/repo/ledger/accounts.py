"""Accounts held in the ledger."""
from __future__ import annotations

import re
from dataclasses import dataclass

ACCOUNT_ID = re.compile(r"^[A-Z][A-Z0-9_]{1,15}$")


@dataclass
class Account:
    """A bank account. ``balance`` and ``overdraft_limit`` are in cents."""

    id: str
    owner: str
    overdraft_limit: int = 0
    frozen: bool = False
    balance: int = 0

    def __post_init__(self) -> None:
        if not ACCOUNT_ID.match(self.id):
            raise ValueError(f"invalid account id {self.id!r}")
        if self.overdraft_limit < 0:
            raise ValueError("overdraft_limit must be >= 0")

    @property
    def floor(self) -> int:
        """Lowest balance, in cents, the account is allowed to reach."""
        return -self.overdraft_limit

    def headroom(self) -> int:
        """How many cents can still be taken out before hitting the floor."""
        return self.balance - self.floor
