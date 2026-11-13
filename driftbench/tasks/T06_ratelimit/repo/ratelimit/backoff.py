"""Retry back-off strategies.

A strategy is a function ``(attempt, **params) -> delay_in_seconds`` where ``attempt`` is 0-based.
"""
from __future__ import annotations

import random
from typing import Callable, Iterator

Strategy = Callable[..., float]


def constant(attempt: int, delay: float = 1.0) -> float:
    """Always wait the same amount of time."""
    _check_attempt(attempt)
    return delay


def linear(attempt: int, step: float = 1.0, cap: float = 30.0) -> float:
    """Wait ``step * (attempt + 1)`` seconds, never more than ``cap``."""
    _check_attempt(attempt)
    return min(cap, step * (attempt + 1))


def exponential(attempt: int, base: float = 0.5, factor: float = 2.0, cap: float = 30.0) -> float:
    """Wait ``base * factor ** attempt`` seconds, never more than ``cap``."""
    _check_attempt(attempt)
    return min(cap, base * factor ** attempt)


def full_jitter(delay: float, rng: random.Random | None = None) -> float:
    """"Full jitter": a uniformly random delay in ``[0, delay]``."""
    rng = rng or random.Random()
    return rng.uniform(0.0, delay)


def delays(n: int, strategy: Strategy = exponential, **params: float) -> Iterator[float]:
    """Yield the delays for the first ``n`` retries of ``strategy``."""
    for attempt in range(n):
        yield strategy(attempt, **params)


def _check_attempt(attempt: int) -> None:
    if attempt < 0:
        raise ValueError("attempt must be >= 0")
