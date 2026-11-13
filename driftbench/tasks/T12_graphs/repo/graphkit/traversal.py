"""Unweighted traversals: BFS, DFS, hop-count shortest paths and connected components."""
from __future__ import annotations

from collections import deque
from typing import Hashable

from .graph import Graph, NodeNotFound


def bfs(graph: Graph, start: Hashable) -> list:
    """Nodes reachable from ``start`` in breadth-first order."""
    if start not in graph:
        raise NodeNotFound(start)
    order, seen, queue = [], {start}, deque([start])
    while queue:
        node = queue.popleft()
        order.append(node)
        for nbr, _ in graph.neighbors(node):
            if nbr not in seen:
                seen.add(nbr)
                queue.append(nbr)
    return order


def dfs(graph: Graph, start: Hashable) -> list:
    """Nodes reachable from ``start`` in depth-first (preorder) order."""
    if start not in graph:
        raise NodeNotFound(start)
    order, seen = [], set()

    def visit(node):
        seen.add(node)
        order.append(node)
        for nbr, _ in graph.neighbors(node):
            if nbr not in seen:
                visit(nbr)

    visit(start)
    return order


def bfs_path(graph: Graph, source: Hashable, target: Hashable) -> list | None:
    """A path with the fewest edges from ``source`` to ``target``, or None."""
    if source not in graph or target not in graph:
        raise NodeNotFound(source if source not in graph else target)
    parent, queue = {source: None}, deque([source])
    while queue:
        node = queue.popleft()
        if node == target:
            path = []
            while node is not None:
                path.append(node)
                node = parent[node]
            return path[::-1]
        for nbr, _ in graph.neighbors(node):
            if nbr not in parent:
                parent[nbr] = node
                queue.append(nbr)
    return None


def connected_components(graph: Graph) -> list[list]:
    """Components of an undirected graph, each in BFS order, in order of first node."""
    seen, components = set(), []
    for node in graph.nodes:
        if node not in seen:
            comp = bfs(graph, node)
            seen.update(comp)
            components.append(comp)
    return components
