import pytest

from ledger import Account


def test_floor_and_headroom():
    acc = Account("ALICE", "Alice", overdraft_limit=5000, balance=1000)
    assert acc.floor == -5000
    assert acc.headroom() == 6000


def test_defaults():
    acc = Account("BOB", "Bob")
    assert (acc.balance, acc.overdraft_limit, acc.frozen) == (0, 0, False)


@pytest.mark.parametrize("bad", ["alice", "A", "WAY_TOO_LONG_ACCOUNT_ID", "A-1"])
def test_invalid_ids(bad):
    with pytest.raises(ValueError):
        Account(bad, "x")


def test_negative_limit():
    with pytest.raises(ValueError):
        Account("ALICE", "Alice", overdraft_limit=-1)
