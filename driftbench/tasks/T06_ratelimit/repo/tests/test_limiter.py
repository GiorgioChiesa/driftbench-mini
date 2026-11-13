import pytest

from ratelimit import FixedWindowLimiter, RateLimitExceeded


def test_fixed_window_allows_up_to_limit(clock):
    lim = FixedWindowLimiter(3, 10, clock)
    assert [lim.allow() for _ in range(4)] == [True, True, True, False]


def test_fixed_window_resets_on_next_window(clock):
    lim = FixedWindowLimiter(1, 10, clock)
    assert lim.allow()
    clock.advance(9.5)
    assert not lim.allow()
    clock.advance(0.5)
    assert lim.allow()


def test_check_raises_with_retry_after(clock):
    lim = FixedWindowLimiter(1, 10, clock)
    lim.check()
    clock.advance(4)
    with pytest.raises(RateLimitExceeded) as info:
        lim.check()
    assert info.value.retry_after == 6.0


def test_from_spec(clock):
    lim = FixedWindowLimiter.from_spec("2/5s", clock)
    assert (lim.limit, lim.window) == (2, 5.0)


@pytest.mark.parametrize("limit, window", [(0, 1), (1, 0), (1, -5)])
def test_invalid_arguments(limit, window):
    with pytest.raises(ValueError):
        FixedWindowLimiter(limit, window)
