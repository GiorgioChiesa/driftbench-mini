"""An adjacency-map graph, directed or undirected, with weighted edges."""
from __future__ import annotations

from typing import Hashable, Iterable, Iterator


class NodeNotFound(KeyError):
    """The node is not in the graph."""


class Graph:
    """Nodes are any hashable values; every edge carries a float weight (default 1.0)."""

    def __init__(self, directed: bool = False):
        self.directed = directed
        self._adj: dict[Hashable, dict[Hashable, float]] = {}

    @classmethod
    def from_edges(cls, edges: Iterable[tuple], directed: bool = False) -> "Graph":
        """Build a graph from ``(u, v)`` or ``(u, v, weight)`` tuples."""
        graph = cls(directed)
        for edge in edges:
            graph.add_edge(*edge)
        return graph

    def add_node(self, node: Hashable) -> None:
        self._adj.setdefault(node, {})

    def add_edge(self, u: Hashable, v: Hashable, weight: float = 1.0) -> None:
        """Add (or re-weight) the edge u -> v; undirected graphs also get v -> u."""
        weight = float(weight)
        self.add_node(u)
        self.add_node(v)
        self._adj[u][v] = weight
        if not self.directed:
            self._adj[v][u] = weight

    def has_edge(self, u: Hashable, v: Hashable) -> bool:
        return v in self._adj.get(u, {})

    def weight(self, u: Hashable, v: Hashable) -> float:
        try:
            return self._adj[u][v]
        except KeyError:
            raise KeyError(f"no edge {u!r} -> {v!r}") from None

    def neighbors(self, node: Hashable) -> Iterator[tuple[Hashable, float]]:
        """``(neighbor, weight)`` pairs of the edges leaving ``node``, in insertion order."""
        if node not in self._adj:
            raise NodeNotFound(node)
        return iter(list(self._adj[node].items()))

    @property
    def nodes(self) -> list:
        return list(self._adj)

    def __contains__(self, node: Hashable) -> bool:
        return node in self._adj

    def edges(self) -> Iterator[tuple[Hashable, Hashable, float]]:
        """Every edge once as ``(u, v, weight)`` (undirected edges are not repeated)."""
        seen = set()
        for u, nbrs in self._adj.items():
            for v, w in nbrs.items():
                if not self.directed:
                    key = frozenset((u, v))
                    if key in seen:
                        continue
                    seen.add(key)
                yield u, v, w

    def degree(self, node: Hashable) -> int:
        if node not in self._adj:
            raise NodeNotFound(node)
        return len(self._adj[node])

    def __repr__(self) -> str:
        kind = "directed" if self.directed else "undirected"
        return f"<Graph {kind} nodes={len(self._adj)} edges={sum(1 for _ in self.edges())}>"
