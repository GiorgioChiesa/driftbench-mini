import pytest

from graphkit import Graph


@pytest.fixture
def city():
    """Undirected road map with integer distances (km)."""
    return Graph.from_edges([
        ("turin", "milan", 140), ("milan", "bologna", 215), ("turin", "genoa", 170),
        ("genoa", "bologna", 290), ("bologna", "florence", 105),
    ])


@pytest.fixture
def grid():
    """A 3 x 4 grid graph whose nodes are (row, col) tuples."""
    rows, cols = 3, 4
    g = Graph()
    for r in range(rows):
        for c in range(cols):
            g.add_node((r, c))
            if c + 1 < cols:
                g.add_edge((r, c), (r, c + 1))
            if r + 1 < rows:
                g.add_edge((r, c), (r + 1, c))
    return g
