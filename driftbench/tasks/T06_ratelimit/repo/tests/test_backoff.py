import random

import pytest

from ratelimit import backoff


def test_constant():
    assert backoff.constant(3, delay=2.0) == 2.0


def test_linear_is_capped():
    assert [backoff.linear(a, step=10.0, cap=25.0) for a in range(4)] == [10.0, 20.0, 25.0, 25.0]


def test_exponential():
    assert list(backoff.delays(5)) == [0.5, 1.0, 2.0, 4.0, 8.0]
    assert backoff.exponential(10, cap=30.0) == 30.0


def test_negative_attempt():
    with pytest.raises(ValueError):
        backoff.exponential(-1)


def test_full_jitter_stays_in_range():
    rng = random.Random(42)
    values = [backoff.full_jitter(4.0, rng) for _ in range(100)]
    assert all(0.0 <= v <= 4.0 for v in values)
    assert len(set(values)) > 50


def test_delays_with_params():
    assert list(backoff.delays(3, backoff.linear, step=2.0)) == [2.0, 4.0, 6.0]
