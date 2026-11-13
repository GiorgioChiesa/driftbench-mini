"""A tiny cooperative scheduler for delayed jobs, driven by an injectable clock."""
from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from typing import Any, Callable

from .clock import Clock, SystemClock


@dataclass(order=True)
class Job:
    due: float
    name: str
    action: Callable[[], Any] = field(compare=False)


class Scheduler:
    """Keeps jobs ordered by due time; :meth:`run_due` runs the ones whose time has come."""

    def __init__(self, clock: Clock | None = None) -> None:
        self.clock = clock or SystemClock()
        self._queue: list[Job] = []

    def call_later(self, delay: float, name: str, action: Callable[[], Any]) -> Job:
        if delay < 0:
            raise ValueError("delay must be >= 0")
        job = Job(self.clock.now() + delay, name, action)
        heapq.heappush(self._queue, job)
        return job

    def cancel(self, name: str) -> bool:
        """Drop every pending job called ``name``; return whether anything was removed."""
        kept = [job for job in self._queue if job.name != name]
        removed = len(kept) != len(self._queue)
        if removed:
            heapq.heapify(kept)
            self._queue = kept
        return removed

    def pending(self) -> list[str]:
        """Names of the pending jobs, in the order they will run."""
        return [job.name for job in sorted(self._queue)]

    def run_due(self) -> list[Any]:
        """Run every job that is due, in due order, and return their results."""
        now = self.clock.now()
        results = []
        while self._queue and self._queue[0].due <= now:
            job = heapq.heappop(self._queue)
            results.append(job.action())
        return results
