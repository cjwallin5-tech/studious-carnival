"""Graph algorithms — STUDENT EXERCISES.

Every function below is a stub that currently raises ``NotImplementedError``.
Your job is to implement them using the ``DirectedGraph`` data structure
(see ``graph.py``). Each one powers a real API endpoint (see
``app/api/routes/graph.py``) and has a matching test in
``tests/test_graph_algorithms.py`` describing the expected behavior.

Reminders about the graph (see ``builder.py`` for the full convention):
    graph.successors(u)   -> the users u follows
    graph.predecessors(u) -> the users who follow u
    graph.neighbors(u)    -> alias for successors(u)
    graph.nodes           -> set of all user ids
    graph.to_undirected() -> a copy where every edge points both ways

You may add private helper functions to this module. Do NOT change the public
function signatures — the API routes and tests depend on them.

Suggested order: all_paths, bfs_shortest_path, degrees_of_separation,
reachable_within, common_neighbors, jaccard_similarity, recommend_users,
connected_components, local_clustering_coefficient, pagerank,
detect_communities.
"""

from collections import deque

from collections.abc import Hashable

from app.graph.graph import DirectedGraph

Node = Hashable


# ---------------------------------------------------------------------------
# EXERCISE 1 — All simple paths (depth-first search)
# ---------------------------------------------------------------------------
def all_paths(
    graph: DirectedGraph, source: Node, target: Node, max_depth: int = 4
) -> list[list[Node]]:
    """Return EVERY simple follow-path from ``source`` to ``target``.

    Find all of them — every distinct route a post could be reshared along
    from ``source`` to ``target`` — up to ``max_depth`` hops long. Use
    **depth-first search (DFS) with backtracking**: walk one route as deep as
    it will go, and when it dead-ends, back up one step and try the next
    branch. (Exercise 2 will answer a related question — just the *shortest*
    route — with a different traversal.)

    A path is *simple* if it never visits the same node twice. That rule is
    what stops DFS from circling a follow-loop forever, and it's why the
    algorithm must *backtrack*: a node blocked on the current path must become
    available again once the search retreats past it.

    Implementation sketch (recursive; an explicit stack also works):
      1. Keep a ``path`` list holding the route walked so far, starting at
         [source].
      2. If the node at the end of ``path`` is ``target``, record a COPY of
         ``path`` (a path of N nodes has N-1 hops; [source] alone covers the
         source == target case).
      3. If ``path`` already spans ``max_depth`` hops, dead end — go back.
      4. Otherwise, for each successor NOT already in ``path``: append it,
         recurse, then pop it off again. That pop is the backtracking step.

    Returns:
        A list of paths, each a list of nodes [source, ..., target], in any
        order. Empty list if target is unreachable within ``max_depth`` hops.

    Raises:
        KeyError if ``source`` is not in the graph. (Do NOT guard with
        ``if source not in graph: return []`` — an unknown source is a
        programming error, not an empty result. An unknown *target*, by
        contrast, is simply unreachable, so it yields the empty list.)

    Complexity: worst case exponential in ``max_depth`` — which is exactly why
    the depth limit exists. (Keep this in mind for Exercise 2, where wanting
    only one shortest path lets a different traversal do far less work.)
    """
    if source == target:
        return [[source]]

    if max_depth == 0:
        return []

    paths = []

    for nodes in graph.neighbors(source):
        for path in all_paths(graph, nodes, target, max_depth - 1):
            if source not in path:
                paths.append([source] + path)

    return paths


# ---------------------------------------------------------------------------
# EXERCISE 2 — Breadth-first shortest path
# ---------------------------------------------------------------------------
def bfs_shortest_path(graph: DirectedGraph, source: Node, target: Node) -> list[Node] | None:
    """Return the shortest follow-path from ``source`` to ``target``.

    Use **breadth-first search (BFS)**. Because every edge has weight 1, the
    first time BFS reaches ``target`` it has found a shortest path. Contrast
    with Exercise 1: DFS dives deep down one branch; BFS explores in expanding
    rings, so it finds the nearest target without enumerating every route.

    Implementation sketch:
      1. If source == target, return [source].
      2. Keep a queue (collections.deque) of nodes to visit, seeded with source.
      3. Keep a `visited` set and a `parent` dict mapping node -> the node we
         came from, so you can reconstruct the path at the end.
      4. Pop from the LEFT of the queue; for each successor not yet visited,
         record its parent and enqueue it. Stop when you dequeue `target`.
      5. Walk the `parent` chain backwards from target to source and reverse it.

    Returns:
        The list of nodes [source, ..., target], or ``None`` if target is
        unreachable from source.

    Raises:
        KeyError if ``source`` is not in the graph. (An unknown ``target`` is
        merely unreachable, so it yields ``None``.j

    Complexity: O(V + E).
    """
    visited: set = set()
    queue = deque([source])
    parent: dict = {}

    if source == target:
        return [source]

    while queue:
        node = queue.popleft()
        if node not in visited:
            visited.add(node)
            for neighbor in graph.neighbors(node):
                if neighbor not in visited:
                    queue.append(neighbor)
                    parent[neighbor] = node
                    if neighbor == target:
                        path = [target]
                        while path[-1] != source:
                            path.append(parent[path[-1]])
                        return path[::-1]


# ---------------------------------------------------------------------------
# EXERCISE 3 — Degrees of separation
# ---------------------------------------------------------------------------
def degrees_of_separation(graph: DirectedGraph, source: Node, target: Node) -> int | None:
    """Return the number of hops on the shortest path source -> target.

    The "2nd-degree connection" idea from LinkedIn. This can reuse
    ``bfs_shortest_path`` (a path of N nodes has N-1 hops), or you can run a
    BFS that tracks distance directly.

    Returns:
        The hop count (0 if source == target), or ``None`` if unreachable.

    Raises:
        KeyError if ``source`` is not in the graph (an unknown ``target`` is
        unreachable, so it yields ``None``).
    """
    hop = bfs_shortest_path(graph, source, target)
    if source == target:
        return 0
    while hop is not None:
        return len(hop) - 1


# ---------------------------------------------------------------------------
# EXERCISE 4 — Reachable set within a depth limit
# ---------------------------------------------------------------------------
def reachable_within(graph: DirectedGraph, source: Node, max_depth: int) -> dict[Node, int]:
    """Return every node reachable from ``source`` within ``max_depth`` hops.

    This is a **level-by-level BFS**. The result maps each reachable node to its
    distance from source. Include the source itself at distance 0. Do not go
    deeper than ``max_depth``.

    Example: with max_depth=2 you get the source (0), everyone it follows (1),
    and everyone *they* follow (2).

    Returns:
        dict mapping node -> distance, for all distances in [0, max_depth].

    Raises:
        KeyError if ``source`` is not in the graph.
    """
    nodes: dict[Node, int] = {source: 0}

    for node in graph.successors(source):
        if max_depth > 0:
            nodes[node] = 1
            for neighbor in graph.successors(node):
                if neighbor not in nodes and max_depth > 1:
                    nodes[neighbor] = 2

    return nodes

    

# ---------------------------------------------------------------------------
# EXERCISE 5 — Common neighbors
# ---------------------------------------------------------------------------
def common_neighbors(graph: DirectedGraph, a: Node, b: Node) -> set[Node]:
    """Return the set of accounts that BOTH ``a`` and ``b`` follow.

    This is a set intersection of their successor sets. It is the building block
    for similarity and recommendations.

    Returns:
        The set of nodes followed by both a and b (may be empty).

    Raises:
        KeyError if ``a`` or ``b`` is not in the graph.
    """
    return graph.successors(a).intersection(graph.successors(b))
     

# ---------------------------------------------------------------------------
# EXERCISE 6 — Jaccard similarity
# ---------------------------------------------------------------------------
def jaccard_similarity(graph: DirectedGraph, a: Node, b: Node) -> float:
    """Return how similar two users are by who they follow, in [0.0, 1.0].

    Jaccard similarity = |intersection| / |union| of their successor sets:

        J(a, b) = |follows(a) ∩ follows(b)| / |follows(a) ∪ follows(b)|

    Edge case: if neither user follows anyone (union is empty), return 0.0.

    Returns:
        A float in [0.0, 1.0]; 1.0 means they follow exactly the same accounts.

    Raises:
        KeyError if ``a`` or ``b`` is not in the graph. (This is distinct from
        the "follows nobody" case, which is a valid input returning 0.0.)
    """
    follows_a = graph.successors(a)
    follows_b = graph.successors(b)

    intersection = follows_a.intersection(follows_b)
    union = follows_a.union(follows_b)
    
    if not union:
        return 0.0
    
    return len(intersection) / len(union)


# ---------------------------------------------------------------------------
# EXERCISE 7 — Friend recommendations ("People you may know")
# ---------------------------------------------------------------------------
def recommend_users(graph: DirectedGraph, user: Node, limit: int = 10) -> list[tuple[Node, int]]:
    """Recommend accounts for ``user`` to follow, best first.

    Classic "friends-of-friends" recommendation:
      - Look at everyone ``user`` already follows (their successors).
      - Look at who *those* people follow (the friends-of-friends).
      - A good candidate is followed by many of the people you follow, so score
        each candidate by how many of your follows also follow them
        (the size of the common-neighbor overlap).
      - EXCLUDE the user themselves and anyone they already follow.
      - Sort by score descending and return the top ``limit``.

    Returns:
        A list of (candidate_node, score) tuples, highest score first,
        at most ``limit`` long.

    Raises:
        KeyError if ``user`` is not in the graph.
    """
    raise NotImplementedError("Exercise 7: implement recommend_users")


# ---------------------------------------------------------------------------
# EXERCISE 8 — Connected components
# ---------------------------------------------------------------------------
def connected_components(graph: DirectedGraph) -> list[set[Node]]:
    """Partition the network into connected components (treat edges as undirected).

    Two users are in the same component if you can get from one to the other by
    following edges in either direction. Use ``graph.to_undirected()`` and then
    repeatedly run a BFS/DFS flood-fill from an unvisited node, collecting every
    node it reaches into one component.

    Returns:
        A list of sets of nodes. Every node appears in exactly one set.
    """
    raise NotImplementedError("Exercise 8: implement connected_components")


# ---------------------------------------------------------------------------
# EXERCISE 9 — Local clustering coefficient
# ---------------------------------------------------------------------------
def local_clustering_coefficient(graph: DirectedGraph, node: Node) -> float:
    """Return the clustering coefficient of ``node`` in [0.0, 1.0].

    "How interconnected are my friends?" Work on the undirected view. If a node
    has k neighbors, there are k*(k-1)/2 possible edges among them. The
    coefficient is:

        (number of edges that actually exist among the neighbors)
        ---------------------------------------------------------------
                        k * (k - 1) / 2

    Edge case: if the node has fewer than 2 neighbors, return 0.0.

    Returns:
        A float in [0.0, 1.0]; 1.0 means all the node's neighbors follow
        each other (a clique).

    Raises:
        KeyError if ``node`` is not in the graph. (Fewer than 2 neighbors is a
        valid input returning 0.0; a node that doesn't exist is not.)
    """
    raise NotImplementedError("Exercise 9: implement local_clustering_coefficient")


# ---------------------------------------------------------------------------
# EXERCISE 10 — PageRank (influence ranking)
# ---------------------------------------------------------------------------
def pagerank(
    graph: DirectedGraph,
    damping: float = 0.85,
    max_iter: int = 100,
    tol: float = 1.0e-6,
) -> dict[Node, float]:
    """Rank users by influence using the **PageRank** algorithm.

    Intuition: you are important if important people follow you. Note the
    direction — a node's rank flows to the nodes it *follows* (its successors).

    Power-iteration sketch:
      1. Let N = number of nodes. Initialise every node's rank to 1/N.
      2. Repeat up to ``max_iter`` times:
           new_rank[v] = (1 - damping)/N
                         + damping * Σ over u that follow v of rank[u]/out_degree(u)
         Handle "dangling" nodes (out_degree 0): distribute their rank evenly
         across all nodes (otherwise rank leaks out of the system).
      3. Stop early when the total change (sum of |new - old|) < ``tol``.

    The returned scores should sum to approximately 1.0.

    Returns:
        dict mapping node -> PageRank score.
    """
    raise NotImplementedError("Exercise 10: implement pagerank")


# ---------------------------------------------------------------------------
# EXERCISE 11 — Community detection (label propagation)
# ---------------------------------------------------------------------------
def detect_communities(graph: DirectedGraph) -> dict[Node, int]:
    """Group users into communities using **label propagation**.

    Work on the undirected view. The algorithm:
      1. Give every node a unique starting label (e.g. its own id).
      2. Repeatedly, for each node, set its label to the one that is most
         common among its neighbors (break ties however you like, but be
         consistent so the algorithm terminates).
      3. Stop when no node changes its label (or after a max number of rounds).
      4. Re-number the resulting labels to 0, 1, 2, ... for a tidy result.

    Returns:
        dict mapping node -> community id (an int). Nodes in the same community
        share the same id.
    """
    raise NotImplementedError("Exercise 11: implement detect_communities")
