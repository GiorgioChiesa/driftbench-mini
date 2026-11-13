import pytest

from graphkit import Graph, NodeNotFound


def test_undirected_edges_are_symmetric(city):
    assert city.has_edge("milan", "turin")
    assert city.weight("bologna", "milan") == 215
    assert len(list(city.edges())) == 5


def test_directed_edges():
    g = Graph.from_edges([("a", "b", 2), ("b", "c")], directed=True)
    assert g.has_edge("a", "b") and not g.has_edge("b", "a")
    assert sorted(g.edges()) == [("a", "b", 2.0), ("b", "c", 1.0)]


def test_neighbors_in_insertion_order(city):
    assert [n for n, _ in city.neighbors("bologna")] == ["milan", "genoa", "florence"]


def test_unknown_node():
    g = Graph()
    with pytest.raises(NodeNotFound):
        list(g.neighbors("x"))
    with pytest.raises(KeyError):
        g.weight("x", "y")


def test_degree_and_contains(grid):
    assert (0, 0) in grid and (3, 0) not in grid
    assert grid.degree((0, 0)) == 2
    assert grid.degree((1, 1)) == 4
