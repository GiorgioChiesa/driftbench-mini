from graphkit import Graph
from graphkit.io import to_dot


def test_u1_dot_weight_labels():
    g = Graph.from_edges([("a", "b", 2.5), ("b", "c")], directed=True)
    out = to_dot(g)
    assert '"a" -> "b" [label="2.5"];' in out
    assert '"b" -> "c" [label="1"];' in out
