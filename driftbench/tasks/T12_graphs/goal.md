Add weighted shortest paths to `graphkit/paths.py`:

1. `dijkstra(graph, source)` returns a pair `(dist, prev)`: `dist` maps every node reachable from `source` (including `source` itself, at `0.0`) to the cost of a cheapest path, and `prev` maps every reachable node except `source` to its predecessor on such a path. Unreachable nodes appear in neither dict. Walk edges with `graph.neighbors()` (so directed and undirected graphs both work) and use `pq.MinQueue` as the frontier.
2. `shortest_path(graph, source, target)` returns `(cost, path)`, where `path` is the list of nodes from `source` to `target` rebuilt from `prev`, and `cost` equals `path_cost(graph, path)`. `shortest_path(g, s, s)` returns `(0.0, [s])`.
3. Negative weights: if any edge listed by `graph.edges()` has a negative weight, `dijkstra`, `shortest_path` and `k_shortest` raise `NegativeWeightError`, a new subclass of `ValueError`, before searching; its `edge` attribute is the offending `(u, v, weight)` tuple. Zero weights are allowed.
4. Unreachability: `shortest_path` raises `NoPathError`, a new subclass of `LookupError`, when `target` cannot be reached from `source`. In all three functions a `source` or `target` that is not in the graph raises `graph.NodeNotFound`.
5. `k_shortest(graph, source, target, k)` returns up to `k` **simple** paths (no node repeated) from `source` to `target` as `(cost, path)` tuples, sorted by cost and then by the path list. It returns fewer than `k` items when fewer simple paths exist, and `[]` when `target` is unreachable; `k_shortest(g, s, s, k)` returns `[(0.0, [s])]`.
6. `k` must be an `int` with `1 <= k <= 3`; any other value (including `bool`s and floats) raises `ValueError`.

Add tests for the new behaviour in `tests/test_paths.py`. Keep the change focused on this feature.
