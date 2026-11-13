# graphkit

Lightweight graph utilities used by the routing and dependency tools: an adjacency-map `Graph`
(directed or undirected, weighted edges), BFS/DFS traversals, a priority queue with decrease-key,
simple metrics and edge-list / Graphviz DOT I/O.

```python
from graphkit import Graph
from graphkit.traversal import bfs_path

g = Graph.from_edges([("a", "b"), ("b", "c")])
bfs_path(g, "a", "c")  # ['a', 'b', 'c']
```

Run the tests with `python -m pytest`.
