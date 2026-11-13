import pytest

from graphkit import Graph, NodeNotFound
from graphkit.traversal import bfs, bfs_path, connected_components, dfs


def test_bfs_order(city):
    assert bfs(city, "turin") == ["turin", "milan", "genoa", "bologna", "florence"]


def test_dfs_order(city):
    assert dfs(city, "turin") == ["turin", "milan", "bologna", "genoa", "florence"]


def test_bfs_visits_whole_grid(grid):
    assert len(bfs(grid, (0, 0))) == 12


def test_bfs_path(grid):
    path = bfs_path(grid, (0, 0), (2, 3))
    assert path[0] == (0, 0) and path[-1] == (2, 3) and len(path) == 6


def test_bfs_path_unreachable():
    g = Graph.from_edges([("a", "b")])
    g.add_node("z")
    assert bfs_path(g, "a", "z") is None
    with pytest.raises(NodeNotFound):
        bfs_path(g, "a", "missing")


def test_connected_components():
    g = Graph.from_edges([("a", "b"), ("c", "d"), ("d", "e")])
    g.add_node("f")
    assert connected_components(g) == [["a", "b"], ["c", "d", "e"], ["f"]]
