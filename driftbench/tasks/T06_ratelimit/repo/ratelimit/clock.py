"""Clock abstractions, so that time-dependent code can be tested deterministically."""
from __future__ import annotations

import time
from typing import Protocol


class Clock(Protocol):
    """Anything with a ``now()`` method returning seconds as a float."""

    def now(self) -> float: ...


class SystemClock:
    """Real clock backed by :func:`time.monotonic` (never goes backwards)."""

    def now(self) -> float:
        return time.monotonic()


class ManualClock:
    """A clock that only moves when told to. Intended for tests and simulations."""

    def __init__(self, start: float = 0.0) -> None:
        self._now = float(start)

    def now(self) -> float:
        return self._now

    def advance(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("cannot move a ManualClock backwards")
        self._now += seconds

    def set(self, timestamp: float) -> None:
        if timestamp < self._now:
            raise ValueError("cannot move a ManualClock backwards")
        self._now = float(timestamp)

    def __repr__(self) -> str:
        return f"ManualClock(now={self._now!r})"
