from ratelimit import Scheduler


def test_runs_only_due_jobs(clock):
    s = Scheduler(clock)
    s.call_later(5, "later", lambda: "L")
    s.call_later(1, "soon", lambda: "S")
    assert s.run_due() == []
    clock.advance(1)
    assert s.run_due() == ["S"]
    clock.advance(10)
    assert s.run_due() == ["L"]
    assert s.pending() == []


def test_pending_order(clock):
    s = Scheduler(clock)
    s.call_later(3, "c", lambda: None)
    s.call_later(1, "a", lambda: None)
    s.call_later(2, "b", lambda: None)
    assert s.pending() == ["a", "b", "c"]


def test_cancel(clock):
    s = Scheduler(clock)
    s.call_later(1, "x", lambda: 1)
    s.call_later(2, "y", lambda: 2)
    assert s.cancel("x") is True
    assert s.cancel("nope") is False
    clock.advance(5)
    assert s.run_due() == [2]


def test_negative_delay(clock):
    import pytest

    with pytest.raises(ValueError):
        Scheduler(clock).call_later(-1, "x", lambda: None)
