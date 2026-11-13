import pytest

from graphkit import Graph
from graphkit.traversal import topological_sort


def test_u3_topological_sort():
    g = Graph.from_edges([("shirt", "tie"), ("tie", "jacket"), ("pants", "shoes"), ("pants", "belt"),
                          ("belt", "jacket")], directed=True)
    order = topological_sort(g)
    assert sorted(order) == sorted(g.nodes)
    for u, v, _ in g.edges():
        assert order.index(u) < order.index(v)
    with pytest.raises(ValueError):
        topological_sort(Graph.from_edges([("a", "b"), ("b", "a")], directed=True))
