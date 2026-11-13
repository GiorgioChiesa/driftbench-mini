"""A min-priority queue with decrease-key, built on heapq (lazy deletion, as in the heapq docs)."""
from __future__ import annotations

import heapq
import itertools
from typing import Hashable

_REMOVED = object()


class MinQueue:
    """Items are hashable and unique; equal priorities pop in insertion order."""

    def __init__(self):
        self._heap: list[list] = []
        self._entries: dict[Hashable, list] = {}
        self._counter = itertools.count()

    def push(self, item: Hashable, priority: float) -> None:
        """Insert ``item``, or lower its priority if it is already queued with a higher one."""
        old = self._entries.get(item)
        if old is not None:
            if old[0] <= priority:
                return
            old[-1] = _REMOVED
        entry = [priority, next(self._counter), item]
        self._entries[item] = entry
        heapq.heappush(self._heap, entry)

    def pop(self) -> tuple[Hashable, float]:
        """Remove and return ``(item, priority)`` with the lowest priority."""
        while self._heap:
            priority, _, item = heapq.heappop(self._heap)
            if item is not _REMOVED:
                del self._entries[item]
                return item, priority
        raise KeyError("pop from an empty queue")

    def priority(self, item: Hashable) -> float:
        return self._entries[item][0]

    def __contains__(self, item: Hashable) -> bool:
        return item in self._entries

    def __len__(self) -> int:
        return len(self._entries)
