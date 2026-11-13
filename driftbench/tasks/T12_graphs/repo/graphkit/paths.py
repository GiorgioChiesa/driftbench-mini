"""Path helpers."""
from __future__ import annotations

from typing import Hashable, Sequence

from .graph import Graph
from .traversal import bfs_path


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
