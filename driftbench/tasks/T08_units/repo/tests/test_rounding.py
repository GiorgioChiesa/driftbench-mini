import pytest

from units.rounding import clamp, round_sig, round_to_step


def test_round_sig():
    assert round_sig(123456, 2) == 120000
    assert round_sig(0.0012345, 3) == 0.00123
    assert round_sig(-98.76, 2) == -99


def test_round_sig_rejects_zero_digits():
    with pytest.raises(ValueError):
        round_sig(1.0, 0)


def test_round_to_step():
    assert round_to_step(7.2, 5) == 5
    assert round_to_step(8, 5) == 10
    with pytest.raises(ValueError):
        round_to_step(1, 0)


def test_clamp():
    assert clamp(5, 0, 3) == 3
    assert clamp(-1, 0, 3) == 0
    with pytest.raises(ValueError):
        clamp(1, 3, 0)
