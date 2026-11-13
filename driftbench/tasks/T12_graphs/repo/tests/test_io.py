import pytest

from graphkit import Graph
from graphkit.io import parse_edge_list, to_dot, to_edge_list


def test_parse_edge_list():
    g = parse_edge_list("a b\nb c 2.5\n\nd\n")
    assert g.nodes == ["a", "b", "c", "d"]
    assert g.weight("c", "b") == 2.5


def test_parse_edge_list_rejects_extra_fields():
    with pytest.raises(ValueError):
        parse_edge_list("a b 1 extra")


def test_round_trip(city):
    again = parse_edge_list(to_edge_list(city))
    def as_set(g):
        return {(frozenset((u, v)), w) for u, v, w in g.edges()}

    assert as_set(again) == as_set(city)


def test_to_dot():
    g = Graph.from_edges([("a", "b")], directed=True)
    g.add_node("z")
    assert to_dot(g) == 'digraph G {\n  "a" -> "b";\n  "z";\n}'
