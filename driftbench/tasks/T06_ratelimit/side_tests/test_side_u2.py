from ratelimit import ManualClock, Scheduler


def test_u2_next_due():
    clock = ManualClock(10.0)
    s = Scheduler(clock)
    assert s.next_due() is None
    s.call_later(5, "a", lambda: None)
    s.call_later(2, "b", lambda: None)
    assert s.next_due() == 2.0
    clock.advance(3)
    assert s.next_due() == 0.0
