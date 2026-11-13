import pytest


def directed_sample():
    from graphkit import Graph

    g = Graph(directed=True)
    for u, v, w in [("s", "a", 1), ("s", "b", 5), ("s", "c", 10), ("a", "b", 1.5), ("b", "c", 2),
                    ("c", "s", 0.5), ("d", "s", 1)]:
        g.add_edge(u, v, w)
    g.add_node("z")
    return g


def test_r1_dijkstra_dist_and_prev():
    from graphkit.paths import dijkstra

    dist, prev = dijkstra(directed_sample(), "s")
    assert dist == {"s": 0.0, "a": 1.0, "b": 2.5, "c": 4.5}
    assert prev == {"a": "s", "b": "a", "c": "b"}
    dist, prev = dijkstra(directed_sample(), "z")
    assert dist == {"z": 0.0} and prev == {}


def test_r2_shortest_path_reconstruction():
    from graphkit import Graph
    from graphkit.paths import path_cost, shortest_path

    g = Graph()  # undirected
    for u, v, w in [("turin", "milan", 1.5), ("milan", "venice", 2.5), ("turin", "genoa", 1.0),
                    ("genoa", "venice", 4.5), ("venice", "trieste", 1.25)]:
        g.add_edge(u, v, w)
    cost, path = shortest_path(g, "trieste", "turin")
    assert path == ["trieste", "venice", "milan", "turin"]
    assert cost == 5.25 == path_cost(g, path)
    assert shortest_path(g, "genoa", "genoa") == (0.0, ["genoa"])
    cost, path = shortest_path(directed_sample(), "s", "c")
    assert (cost, path) == (4.5, ["s", "a", "b", "c"])


def test_r3_negative_weights():
    from graphkit import Graph
    from graphkit.paths import NegativeWeightError, dijkstra, k_shortest, shortest_path

    assert issubclass(NegativeWeightError, ValueError)
    g = Graph(directed=True)
    g.add_edge("a", "b", 2)
    g.add_edge("x", "y", -1)  # not even reachable from "a": still rejected
    for call in (lambda: dijkstra(g, "a"), lambda: shortest_path(g, "a", "b"), lambda: k_shortest(g, "a", "b", 2)):
        with pytest.raises(NegativeWeightError) as info:
            call()
        assert tuple(info.value.edge) == ("x", "y", -1.0)
    zero = Graph.from_edges([("a", "b", 0), ("b", "c", 0)])
    assert shortest_path(zero, "a", "c") == (0.0, ["a", "b", "c"])


def test_r4_unreachable_and_unknown_nodes():
    from graphkit import NodeNotFound
    from graphkit.paths import NoPathError, dijkstra, k_shortest, shortest_path

    assert issubclass(NoPathError, LookupError)
    g = directed_sample()
    with pytest.raises(NoPathError):
        shortest_path(g, "s", "z")
    with pytest.raises(NoPathError):
        shortest_path(g, "s", "d")  # edge d -> s only
    for call in (lambda: dijkstra(g, "nope"), lambda: shortest_path(g, "nope", "s"),
                 lambda: shortest_path(g, "s", "nope"), lambda: k_shortest(g, "s", "nope", 1)):
        with pytest.raises(NodeNotFound):
            call()


def test_r5_k_shortest_simple_paths():
    from graphkit import Graph
    from graphkit.paths import k_shortest

    g = Graph.from_edges([("s", "a", 1), ("a", "t", 1), ("s", "b", 1), ("b", "t", 2), ("a", "b", 0.5)])
    assert k_shortest(g, "s", "t", 3) == [(2.0, ["s", "a", "t"]), (2.5, ["s", "b", "a", "t"]), (3.0, ["s", "b", "t"])]
    assert k_shortest(g, "s", "t", 1) == [(2.0, ["s", "a", "t"])]
    tie = Graph.from_edges([("s", "y", 1), ("y", "t", 1), ("s", "x", 1), ("x", "t", 1)])
    assert k_shortest(tie, "s", "t", 2) == [(2.0, ["s", "x", "t"]), (2.0, ["s", "y", "t"])]
    line = Graph.from_edges([("s", "m", 1), ("m", "t", 1), ("t", "m", 1), ("m", "s", 1)], directed=True)
    assert k_shortest(line, "s", "t", 3) == [(2.0, ["s", "m", "t"])]
    assert k_shortest(directed_sample(), "s", "z", 2) == []
    assert k_shortest(g, "s", "s", 3) == [(0.0, ["s"])]


def test_r6_k_validation():
    from graphkit import Graph
    from graphkit.paths import k_shortest

    g = Graph.from_edges([("s", "t", 1)])
    for bad in (0, 4, -1, True, 2.0, "2", None):
        with pytest.raises(ValueError):
            k_shortest(g, "s", "t", bad)
    assert k_shortest(g, "s", "t", 3) == [(1.0, ["s", "t"])]
