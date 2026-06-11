# Graph Exercises

This project includes an in-memory graph built from the social network's
**follow** relationships. Both the data structure AND the algorithms are the
assignment: first you build `DirectedGraph` itself (Exercise 0), then you
implement ten algorithms on top of it.

## The pieces

| File | What it is |
|------|------------|
| `app/graph/graph.py` | `DirectedGraph` — **Exercise 0, do this first.** The class skeleton, docstrings, and internal representation are given; every method is a stub. Nothing else works until this does. |
| `tests/test_graph_structure.py` | The spec for Exercise 0 — one test class per step, ordered so you can implement and verify one step at a time. |
| `app/graph/builder.py` | Turns the `follows` table into a `DirectedGraph`. Already done. |
| `app/graph/algorithms.py` | Ten stubbed algorithm functions, each raising `NotImplementedError`. |
| `app/api/routes/graph.py` | API endpoints already wired to each algorithm. They return **501** until the code underneath works, then start returning real data. |
| `tests/test_graph_algorithms.py` | One acceptance test per algorithm exercise (currently `xfail`). This is your spec. |

## Exercise 0 — the data structure

`DirectedGraph` stores the network as an adjacency list (two dictionaries —
the file's docstring explains the representation). Implement its methods in
the numbered steps below; each step has a matching test class, so you can
work strictly test-by-test:

```bash
pytest tests/test_graph_structure.py -k Step01   # then Step02, Step03, ...
```

| Step | Methods | Test class |
|------|---------|------------|
| 01 | `add_node`, `has_node` | `TestStep01AddNode` |
| 02 | `add_edge`, `has_edge` | `TestStep02AddEdge` |
| 03 | `nodes`, `number_of_nodes` | `TestStep03Nodes` |
| 04 | `successors`, `predecessors` | `TestStep04SuccessorsPredecessors` |
| 05 | `out_degree`, `in_degree` | `TestStep05Degrees` |
| 06 | `edges`, `number_of_edges` | `TestStep06Edges` |
| 07 | `remove_edge` | `TestStep07RemoveEdge` |
| 08 | `remove_node` | `TestStep08RemoveNode` |
| 09 | `to_undirected` | `TestStep09ToUndirected` |
| 10 | — (integration) | `TestStep10FullScenario` |

When the whole file passes —

```bash
pytest tests/test_graph_structure.py
```

— the graph is complete and everything downstream (builder, algorithms,
API endpoints, frontend) can use it. Until then, **every** `/graph` endpoint
returns 501, no matter how many algorithms you've written.

## Edge-direction convention

An edge `A -> B` means **"A follows B"**. So for a node `u`:

- `graph.successors(u)` → the users `u` **follows**
- `graph.predecessors(u)` → the users who **follow** `u`
- `graph.neighbors(u)` → alias for `successors(u)`
- `graph.to_undirected()` → a copy where every edge points both ways

## The algorithm exercises

| # | Function | Algorithm | Powers endpoint |
|---|----------|-----------|-----------------|
| 1 | `bfs_shortest_path` | Breadth-first search | `GET /graph/users/{a}/path/{b}` |
| 2 | `degrees_of_separation` | BFS distance | `GET /graph/users/{a}/degrees/{b}` |
| 3 | `reachable_within` | Level-limited BFS | `GET /graph/users/{id}/reachable` |
| 4 | `common_neighbors` | Set intersection | `GET /graph/users/{id}/mutuals/{other}` |
| 5 | `jaccard_similarity` | Jaccard index | `GET /graph/users/{id}/similarity/{other}` |
| 6 | `recommend_users` | Friends-of-friends ranking | `GET /graph/users/{id}/recommendations` |
| 7 | `connected_components` | Flood-fill / union of BFS | `GET /graph/components` |
| 8 | `local_clustering_coefficient` | Triangle counting | `GET /graph/users/{id}/clustering` |
| 9 | `pagerank` | Power iteration | `GET /graph/influencers` |
| 10 | `detect_communities` | Label propagation | `GET /graph/communities` |

Suggested order is easiest-first: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10.

## Workflow

0. Finish Exercise 0 first (see above) — the algorithm tests build
   `DirectedGraph` instances, so none of them can pass before the structure
   works.
1. Open `app/graph/algorithms.py` and read the docstring for an exercise — each
   one has an implementation sketch.
2. Implement it (you may add private helper functions; don't change the public
   signatures — the routes and tests depend on them).
3. In `tests/test_graph_algorithms.py`, delete the `@pytest.mark.xfail(...)`
   line above the matching test and run it:

   ```bash
   pytest -k bfs_shortest_path
   ```

4. Start the API and watch the endpoint go from `501` to real data:

   ```bash
   uvicorn app.main:app --reload
   # then open http://localhost:8000/docs and try the /graph routes
   ```

## Stretch goals

- Bidirectional BFS for `bfs_shortest_path` on large graphs.
- Cache the built graph in `builder.py` and invalidate on follow/unfollow.
- Add **strongly** connected components (Tarjan/Kosaraju) — note the difference
  from the weakly-connected `connected_components` in exercise 7.
- Build a second graph from likes/comments (an "engagement graph") and run the
  same algorithms on it.
