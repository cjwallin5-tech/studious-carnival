"""Acceptance tests for the graph algorithm exercises.

Every test is marked ``xfail`` because the algorithms start out unimplemented
(they raise NotImplementedError). They double as the *spec*: each test builds a
small graph by hand and asserts the exact expected result.

WORKFLOW FOR STUDENTS:
  1. Pick an exercise in app/graph/algorithms.py and implement it.
  2. Delete the `@pytest.mark.xfail(...)` line above the matching test.
  3. Run `pytest -k <test_name>` and make it pass.

(With xfail, an unimplemented test shows as "xfailed" and a correctly
implemented one shows as "xpassed" — either way the suite stays green, so you
can also just watch for xpasses.)
"""

import pytest

from app.graph import algorithms
from app.graph.graph import DirectedGraph


def _graph(edges: list[tuple[int, int]], isolated: list[int] | None = None) -> DirectedGraph:
    g = DirectedGraph()
    for u, v in edges:
        g.add_edge(u, v)
    for node in isolated or []:
        g.add_node(node)
    return g


# --- Exercise 1: bfs_shortest_path ----------------------------------------


@pytest.mark.xfail(raises=NotImplementedError, reason="implement bfs_shortest_path")
def test_bfs_shortest_path_finds_shortest() -> None:
    # 1->5->4 (2 hops) is shorter than 1->2->3->4 (3 hops).
    g = _graph([(1, 2), (2, 3), (3, 4), (1, 5), (5, 4)])
    assert algorithms.bfs_shortest_path(g, 1, 4) == [1, 5, 4]


@pytest.mark.xfail(raises=NotImplementedError, reason="implement bfs_shortest_path")
def test_bfs_shortest_path_same_node() -> None:
    g = _graph([(1, 2)])
    assert algorithms.bfs_shortest_path(g, 1, 1) == [1]


@pytest.mark.xfail(raises=NotImplementedError, reason="implement bfs_shortest_path")
def test_bfs_shortest_path_unreachable() -> None:
    g = _graph([(1, 2), (2, 3)])
    assert algorithms.bfs_shortest_path(g, 3, 1) is None


# --- Exercise 2: degrees_of_separation ------------------------------------


@pytest.mark.xfail(raises=NotImplementedError, reason="implement degrees_of_separation")
def test_degrees_of_separation() -> None:
    g = _graph([(1, 2), (2, 3), (3, 4), (1, 5), (5, 4)])
    assert algorithms.degrees_of_separation(g, 1, 4) == 2
    assert algorithms.degrees_of_separation(g, 1, 1) == 0
    assert algorithms.degrees_of_separation(g, 4, 1) is None


# --- Exercise 3: reachable_within -----------------------------------------


@pytest.mark.xfail(raises=NotImplementedError, reason="implement reachable_within")
def test_reachable_within() -> None:
    g = _graph([(1, 2), (1, 3), (2, 4), (2, 5), (3, 4)])
    assert algorithms.reachable_within(g, 1, 1) == {1: 0, 2: 1, 3: 1}
    assert algorithms.reachable_within(g, 1, 2) == {1: 0, 2: 1, 3: 1, 4: 2, 5: 2}


# --- Exercise 4: common_neighbors -----------------------------------------


@pytest.mark.xfail(raises=NotImplementedError, reason="implement common_neighbors")
def test_common_neighbors() -> None:
    g = _graph([(1, 2), (1, 3), (1, 5), (4, 2), (4, 3), (4, 6)])
    assert algorithms.common_neighbors(g, 1, 4) == {2, 3}


# --- Exercise 5: jaccard_similarity ---------------------------------------


@pytest.mark.xfail(raises=NotImplementedError, reason="implement jaccard_similarity")
def test_jaccard_similarity() -> None:
    g = _graph([(1, 2), (1, 3), (1, 5), (4, 2), (4, 3), (4, 6)], isolated=[7, 8])
    # intersection {2,3} (size 2), union {2,3,5,6} (size 4)
    assert algorithms.jaccard_similarity(g, 1, 4) == 0.5
    # neither follows anyone -> defined as 0.0
    assert algorithms.jaccard_similarity(g, 7, 8) == 0.0


# --- Exercise 6: recommend_users ------------------------------------------


@pytest.mark.xfail(raises=NotImplementedError, reason="implement recommend_users")
def test_recommend_users() -> None:
    # 1 follows {2,3}. 2 follows {4,5}, 3 follows {4}.
    # 4 is reachable via both 2 and 3 (score 2); 5 via 2 only (score 1).
    g = _graph([(1, 2), (1, 3), (2, 4), (2, 5), (3, 4)])
    recs = algorithms.recommend_users(g, 1, limit=10)
    assert recs[0] == (4, 2)
    assert dict(recs) == {4: 2, 5: 1}
    # never recommend yourself or people you already follow
    recommended = {uid for uid, _ in recs}
    assert recommended.isdisjoint({1, 2, 3})


# --- Exercise 7: connected_components -------------------------------------


@pytest.mark.xfail(raises=NotImplementedError, reason="implement connected_components")
def test_connected_components() -> None:
    g = _graph([(1, 2), (2, 3), (3, 4), (1, 5), (5, 4), (10, 11)], isolated=[20])
    components = {frozenset(c) for c in algorithms.connected_components(g)}
    assert components == {
        frozenset({1, 2, 3, 4, 5}),
        frozenset({10, 11}),
        frozenset({20}),
    }


# --- Exercise 8: local_clustering_coefficient -----------------------------


@pytest.mark.xfail(raises=NotImplementedError, reason="implement local_clustering_coefficient")
def test_local_clustering_coefficient() -> None:
    # Undirected neighbors of 1 are {2,3,4}; only the 2-3 edge exists among them.
    g = _graph([(1, 2), (1, 3), (2, 3), (1, 4)])
    assert algorithms.local_clustering_coefficient(g, 1) == pytest.approx(1 / 3)
    # node 4 has a single neighbor -> 0.0
    assert algorithms.local_clustering_coefficient(g, 4) == 0.0


# --- Exercise 9: pagerank -------------------------------------------------


@pytest.mark.xfail(raises=NotImplementedError, reason="implement pagerank")
def test_pagerank() -> None:
    # Everyone follows node 1, so node 1 should rank highest.
    g = _graph([(2, 1), (3, 1), (4, 1), (1, 2)])
    ranks = algorithms.pagerank(g)
    assert set(ranks.keys()) == {1, 2, 3, 4}
    assert sum(ranks.values()) == pytest.approx(1.0, abs=1e-3)
    assert max(ranks, key=ranks.get) == 1


# --- Exercise 10: detect_communities --------------------------------------


@pytest.mark.xfail(raises=NotImplementedError, reason="implement detect_communities")
def test_detect_communities() -> None:
    # Two separate cliques: {1,2,3} and {4,5}.
    g = _graph([(1, 2), (2, 1), (2, 3), (3, 2), (1, 3), (3, 1), (4, 5), (5, 4)])
    labels = algorithms.detect_communities(g)
    assert labels[1] == labels[2] == labels[3]
    assert labels[4] == labels[5]
    assert labels[1] != labels[4]
    assert len(set(labels.values())) == 2
