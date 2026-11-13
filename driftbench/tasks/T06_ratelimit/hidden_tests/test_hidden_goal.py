import pytest


def test_r1_constructor_and_validation():
    from ratelimit.clock import ManualClock, SystemClock
    from ratelimit.limiter import SlidingWindowLimiter

    clock = ManualClock(5.0)
    lim = SlidingWindowLimiter(3, 2, clock)
    assert lim.limit == 3
    assert lim.window == 2.0 and isinstance(lim.window, float)
    assert lim.clock is clock
    assert isinstance(SlidingWindowLimiter(1, 1).clock, SystemClock)
    for limit, window in [(0, 1), (-1, 1), (1, 0), (1, -0.5)]:
        with pytest.raises(ValueError):
            SlidingWindowLimiter(limit, window, clock)


def test_r2_sliding_window_expiry():
    from ratelimit.clock import ManualClock
    from ratelimit.limiter import SlidingWindowLimiter

    clock = ManualClock(100.0)
    lim = SlidingWindowLimiter(2, 1.0, clock)
    assert lim.allow("k") is True          # hit at 100.0
    clock.advance(0.5)
    assert lim.allow("k") is True          # hit at 100.5
    assert lim.allow("k") is False         # refused, not recorded
    clock.advance(0.5)                     # 101.0: first hit expires exactly now
    assert lim.allow("k") is True          # hit at 101.0
    assert lim.allow("k") is False
    clock.advance(0.25)                    # 101.25: 100.5 still counts (fixed windows would reset)
    assert lim.allow("k") is False
    clock.advance(0.25)                    # 101.5: 100.5 expires
    assert lim.allow("k") is True


def test_r3_per_key_buckets():
    from ratelimit.clock import ManualClock
    from ratelimit.limiter import SlidingWindowLimiter

    clock = ManualClock(0.0)
    lim = SlidingWindowLimiter(1, 10.0, clock)
    assert lim.allow("alice") is True
    assert lim.allow("alice") is False
    assert lim.allow("bob") is True
    assert lim.allow(("ip", "10.0.0.1")) is True
    assert lim.allow("bob") is False


def test_r4_retry_after():
    from ratelimit.clock import ManualClock
    from ratelimit.limiter import SlidingWindowLimiter

    clock = ManualClock(0.0)
    lim = SlidingWindowLimiter(2, 10.0, clock)
    assert lim.retry_after("new") == 0.0
    lim.allow("k")
    assert lim.retry_after("k") == 0.0
    clock.advance(2.5)
    lim.allow("k")
    assert lim.retry_after("k") == pytest.approx(7.5)
    clock.advance(7.0)
    assert lim.retry_after("k") == pytest.approx(0.5)
    clock.advance(0.5)
    assert lim.retry_after("k") == 0.0
    assert lim.allow("k") is True
    assert lim.retry_after("k") == pytest.approx(2.5)


def test_r5_reset():
    from ratelimit.clock import ManualClock
    from ratelimit.limiter import SlidingWindowLimiter

    clock = ManualClock(0.0)
    lim = SlidingWindowLimiter(1, 60.0, clock)
    lim.allow("a")
    lim.allow("b")
    lim.reset("a")
    assert lim.allow("a") is True
    assert lim.allow("b") is False
    lim.reset("never-seen")
    lim.reset()
    assert lim.allow("a") is True
    assert lim.allow("b") is True


def test_r6_from_spec():
    from ratelimit.clock import ManualClock
    from ratelimit.limiter import SlidingWindowLimiter

    clock = ManualClock(0.0)
    lim = SlidingWindowLimiter.from_spec("3/2s", clock=clock)
    assert isinstance(lim, SlidingWindowLimiter)
    assert (lim.limit, lim.window, lim.clock) == (3, 2.0, clock)
    assert [lim.allow("x") for _ in range(4)] == [True, True, True, False]
    clock.advance(2)
    assert lim.allow("x") is True
    assert SlidingWindowLimiter.from_spec("10/min").window == 60.0
    with pytest.raises(ValueError):
        SlidingWindowLimiter.from_spec("lots/min")
