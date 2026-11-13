import pytest

from ratelimit import ManualClock, SystemClock


def test_advance(clock):
    clock.advance(2.5)
    assert clock.now() == 1_002.5


def test_starts_at_given_time(clock):
    assert clock.now() == 1_000.0


def test_set(clock):
    clock.set(1_010)
    assert clock.now() == 1_010.0


def test_cannot_go_backwards(clock):
    with pytest.raises(ValueError):
        clock.advance(-1)
    with pytest.raises(ValueError):
        clock.set(999)


def test_system_clock_is_monotonic():
    c = SystemClock()
    assert c.now() <= c.now()


def test_repr():
    assert repr(ManualClock(3)) == "ManualClock(now=3.0)"
