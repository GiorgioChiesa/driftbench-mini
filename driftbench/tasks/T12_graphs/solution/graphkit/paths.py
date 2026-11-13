"""Path helpers: path costs, hop distances and weighted shortest paths (Dijkstra)."""
from __future__ import annotations

import heapq
from typing import Hashable, Sequence

from .graph import Graph, NodeNotFound
from .pq import MinQueue
from .traversal import bfs_path


class NegativeWeightError(ValueError):
    """Dijkstra-based searches require non-negative edge weights."""

    def __init__(self, edge: tuple):
        u, v, w = edge
        super().__init__(f"negative weight {w} on edge {u!r} -> {v!r}")
        self.edge = edge


class NoPathError(LookupError):
    """The target cannot be reached from the source."""


def path_cost(graph: Graph, path: Sequence[Hashable]) -> float:
    """Sum of the edge weights along ``path`` (0.0 for a single node)."""
    total = 0.0
    for u, v in zip(path, path[1:]):
        total += graph.weight(u, v)
    return total


def hop_distance(graph: Graph, source: Hashable, target: Hashable) -> int | None:
    """Number of edges on the shortest unweighted path, or None if unreachable."""
    path = bfs_path(graph, source, target)
    return None if path is None else len(path) - 1


def _check(graph: Graph, *nodes: Hashable) -> None:
    for node in nodes:
        if node not in graph:
            raise NodeNotFound(node)
    for u, v, w in graph.edges():
        if w < 0:
            raise NegativeWeightError((u, v, w))


def dijkstra(graph: Graph, source: Hashable) -> tuple[dict, dict]:
    """Shortest-path costs ``dist`` and predecessors ``prev`` for every node reachable from ``source``."""
    _check(graph, source)
    dist, prev, best = {}, {}, {source: 0.0}
    queue = MinQueue()
    queue.push(source, 0.0)
    while queue:
        node, cost = queue.pop()
        dist[node] = cost
        for nbr, w in graph.neighbors(node):
            if nbr in dist:
                continue
            candidate = cost + w
            if candidate < best.get(nbr, float("inf")):
                best[nbr] = candidate
                prev[nbr] = node
                queue.push(nbr, candidate)
    return dist, prev


def shortest_path(graph: Graph, source: Hashable, target: Hashable) -> tuple[float, list]:
    """``(cost, path)`` of a cheapest path from ``source`` to ``target``."""
    _check(graph, source, target)
    dist, prev = dijkstra(graph, source)
    if target not in dist:
        raise NoPathError(f"{target!r} is not reachable from {source!r}")
    path = [target]
    while path[-1] != source:
        path.append(prev[path[-1]])
    path.reverse()
    return dist[target], path


def k_shortest(graph: Graph, source: Hashable, target: Hashable, k: int) -> list[tuple[float, list]]:
    """Up to ``k`` (1..3) cheapest simple paths, sorted by cost and then by node sequence."""
    if isinstance(k, bool) or not isinstance(k, int) or not 1 <= k <= 3:
        raise ValueError(f"k must be an int between 1 and 3, got {k!r}")
    _check(graph, source, target)
    if source == target:
        return [(0.0, [source])]
    found: list[tuple[float, list]] = []
    heap: list[tuple[float, list]] = [(0.0, [source])]
    while heap and len(found) < k:
        cost, path = heapq.heappop(heap)
        node = path[-1]
        if node == target:
            found.append((cost, path))
            continue
        for nbr, w in graph.neighbors(node):
            if nbr not in path:
                heapq.heappush(heap, (cost + w, path + [nbr]))
    return found
