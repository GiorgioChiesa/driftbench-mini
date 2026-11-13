import pytest

from graphkit.paths import hop_distance, path_cost


def test_path_cost(city):
    assert path_cost(city, ["turin", "milan", "bologna"]) == 355
    assert path_cost(city, ["turin"]) == 0.0


def test_path_cost_missing_edge(city):
    with pytest.raises(KeyError):
        path_cost(city, ["turin", "florence"])


def test_hop_distance(city, grid):
    assert hop_distance(city, "turin", "florence") == 3
    assert hop_distance(grid, (0, 0), (0, 0)) == 0
