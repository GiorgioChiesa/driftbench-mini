"""Simple structural metrics."""
from __future__ import annotations

from collections import Counter

from .graph import Graph


def edge_count(graph: Graph) -> int:
    return sum(1 for _ in graph.edges())


def density(graph: Graph) -> float:
    """Edges present divided by edges possible (no self-loops)."""
    n = len(graph.nodes)
    possible = n * (n - 1) if graph.directed else n * (n - 1) / 2
    return edge_count(graph) / possible


def degree_histogram(graph: Graph) -> dict[int, int]:
    """``{degree: number of nodes with that degree}``, sorted by degree."""
    return dict(sorted(Counter(graph.degree(n) for n in graph.nodes).items()))


def hubs(graph: Graph, n: int = 3) -> list:
    """The ``n`` nodes with the highest degree (ties: insertion order)."""
    return sorted(graph.nodes, key=graph.degree, reverse=True)[:n]
