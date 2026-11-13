from graphkit import Graph
from graphkit.metrics import average_degree


def test_u2_average_degree():
    g = Graph.from_edges([("a", "b"), ("b", "c"), ("c", "a"), ("c", "d")])
    assert average_degree(g) == 2.0
    assert average_degree(Graph()) == 0.0
