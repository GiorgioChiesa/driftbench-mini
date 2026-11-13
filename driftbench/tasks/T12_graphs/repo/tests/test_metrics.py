from graphkit import Graph
from graphkit.metrics import degree_histogram, density, edge_count, hubs


def test_edge_count_and_density(grid):
    assert edge_count(grid) == 17
    assert density(grid) == 17 / 66


def test_directed_density():
    g = Graph.from_edges([("a", "b"), ("b", "a")], directed=True)
    assert density(g) == 1.0


def test_degree_histogram(grid):
    assert degree_histogram(grid) == {2: 4, 3: 6, 4: 2}


def test_hubs(city):
    assert hubs(city, 1) == ["bologna"]
