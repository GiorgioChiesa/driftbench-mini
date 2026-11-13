from datetime import date

import pytest

from ledger import Ledger


@pytest.fixture
def book():
    led = Ledger()
    led.open_account("ALICE", "Alice")
    led.open_account("BOB", "Bob", overdraft_limit="50.00")
    led.deposit("ALICE", "100.00", date(2024, 1, 1))
    return led
