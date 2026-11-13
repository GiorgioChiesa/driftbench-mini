"""Reading edge lists and writing Graphviz DOT."""
from __future__ import annotations

from .graph import Graph


def parse_edge_list(text: str, directed: bool = False) -> Graph:
    """Parse lines of ``u v`` or ``u v weight``; blank lines are ignored."""
    graph = Graph(directed)
    for lineno, line in enumerate(text.splitlines(), start=1):
        fields = line.split()
        if not fields:
            continue
        if len(fields) == 1:
            graph.add_node(fields[0])
        elif len(fields) in (2, 3):
            graph.add_edge(*fields[:2], float(fields[2]) if len(fields) == 3 else 1.0)
        else:
            raise ValueError(f"line {lineno}: expected 'u v [weight]', got {line!r}")
    return graph


def to_edge_list(graph: Graph) -> str:
    return "\n".join(f"{u} {v} {w:g}" for u, v, w in graph.edges())


def to_dot(graph: Graph, name: str = "G") -> str:
    """Graphviz source; isolated nodes are listed too."""
    kind, arrow = ("digraph", "->") if graph.directed else ("graph", "--")
    lines = [f"{kind} {name} {{"]
    linked = set()
    for u, v, _ in graph.edges():
        lines.append(f'  "{u}" {arrow} "{v}";')
        linked.update((u, v))
    lines += [f'  "{n}";' for n in graph.nodes if n not in linked]
    lines.append("}")
    return "\n".join(lines)
