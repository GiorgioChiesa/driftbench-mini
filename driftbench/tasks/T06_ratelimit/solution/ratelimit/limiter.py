"""Rate limiters."""
from __future__ import annotations

from collections import deque
from typing import Hashable

from .clock import Clock, SystemClock
from .config import parse_rate


class RateLimitExceeded(Exception):
    """Raised by :meth:`FixedWindowLimiter.check` when no call is allowed right now."""

    def __init__(self, retry_after: float) -> None:
        super().__init__(f"rate limit exceeded, retry in {retry_after:.2f}s")
        self.retry_after = retry_after


class FixedWindowLimiter:
    """At most ``limit`` calls per window of ``window`` seconds, for a single caller.

    Windows are aligned to multiples of ``window`` on the clock's time line, so a burst at the
    end of one window can be followed immediately by another burst in the next one.
    """

    def __init__(self, limit: int, window: float, clock: Clock | None = None) -> None:
        if limit < 1:
            raise ValueError("limit must be >= 1")
        if window <= 0:
            raise ValueError("window must be > 0")
        self.limit = limit
        self.window = float(window)
        self.clock = clock or SystemClock()
        self._window_start: float | None = None
        self._count = 0

    @classmethod
    def from_spec(cls, spec: str, clock: Clock | None = None) -> "FixedWindowLimiter":
        """Build a limiter from a rate spec such as ``"10/min"``."""
        rate = parse_rate(spec)
        return cls(rate.limit, rate.window, clock)

    def _roll(self) -> float:
        now = self.clock.now()
        start = now - (now % self.window)
        if start != self._window_start:
            self._window_start = start
            self._count = 0
        return now

    def allow(self) -> bool:
        """Record a call and return True if it fits in the current window."""
        self._roll()
        if self._count < self.limit:
            self._count += 1
            return True
        return False

    def check(self) -> None:
        """Like :meth:`allow`, but raise :class:`RateLimitExceeded` instead of returning False."""
        if not self.allow():
            now = self.clock.now()
            raise RateLimitExceeded(self._window_start + self.window - now)


class SlidingWindowLimiter:
    """At most ``limit`` calls per key in any interval of ``window`` seconds."""

    def __init__(self, limit: int, window: float, clock: Clock | None = None) -> None:
        if limit < 1:
            raise ValueError("limit must be >= 1")
        if window <= 0:
            raise ValueError("window must be > 0")
        self.limit = limit
        self.window = float(window)
        self.clock = clock or SystemClock()
        self._hits: dict[Hashable, deque[float]] = {}

    @classmethod
    def from_spec(cls, spec: str, clock: Clock | None = None) -> "SlidingWindowLimiter":
        rate = parse_rate(spec)
        return cls(rate.limit, rate.window, clock)

    def _bucket(self, key: Hashable, now: float) -> deque[float]:
        hits = self._hits.setdefault(key, deque())
        while hits and hits[0] + self.window <= now:
            hits.popleft()
        return hits

    def allow(self, key: Hashable) -> bool:
        now = self.clock.now()
        hits = self._bucket(key, now)
        if len(hits) < self.limit:
            hits.append(now)
            return True
        return False

    def retry_after(self, key: Hashable) -> float:
        now = self.clock.now()
        hits = self._bucket(key, now)
        if len(hits) < self.limit:
            return 0.0
        return hits[0] + self.window - now

    def reset(self, key: Hashable | None = None) -> None:
        if key is None:
            self._hits.clear()
        else:
            self._hits.pop(key, None)
