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


# --- Exercise 1: all_paths (DFS) -------------------------------------------


@pytest.mark.xfail(raises=NotImplementedError, reason="implement all_paths")
def test_all_paths_finds_every_route() -> None:
    # Three simple routes from 1 to 4: 1->2->4, 1->3->4, and 1->2->3->4.
    g = _graph([(1, 2), (1, 3), (2, 3), (2, 4), (3, 4)])
    paths = {tuple(p) for p in algorithms.all_paths(g, 1, 4, max_depth=4)}
    assert paths == {(1, 2, 4), (1, 3, 4), (1, 2, 3, 4)}


@pytest.mark.xfail(raises=NotImplementedError, reason="implement all_paths")
def test_all_paths_respects_max_depth() -> None:
    g = _graph([(1, 2), (1, 3), (2, 3), (2, 4), (3, 4)])
    # With only 2 hops allowed, the 3-hop route 1->2->3->4 must be excluded.
    paths = {tuple(p) for p in algorithms.all_paths(g, 1, 4, max_depth=2)}
    assert paths == {(1, 2, 4), (1, 3, 4)}


@pytest.mark.xfail(raises=NotImplementedError, reason="implement all_paths")
def test_all_paths_handles_cycles() -> None:
    # 1->2->3->1 is a follow-loop; simple paths must not get stuck in it.
    g = _graph([(1, 2), (2, 3), (3, 1), (2, 4)])
    paths = {tuple(p) for p in algorithms.all_paths(g, 1, 4, max_depth=4)}
    assert paths == {(1, 2, 4)}


@pytest.mark.xfail(raises=NotImplementedError, reason="implement all_paths")
def test_all_paths_edge_cases() -> None:
    g = _graph([(1, 2), (2, 3)])
    # source == target -> the trivial zero-hop path
    assert algorithms.all_paths(g, 1, 1, max_depth=3) == [[1]]
    # unreachable -> no paths at all
    assert algorithms.all_paths(g, 3, 1, max_depth=3) == []


@pytest.mark.xfail(raises=NotImplementedError, reason="implement all_paths")
def test_all_paths_includes_direct_edge() -> None:
    # The 1-hop route 1->4 and the 2-hop route 1->2->4 are both valid.
    g = _graph([(1, 2), (2, 4), (1, 4)])
    paths = {tuple(p) for p in algorithms.all_paths(g, 1, 4, max_depth=4)}
    assert paths == {(1, 4), (1, 2, 4)}


@pytest.mark.xfail(raises=NotImplementedError, reason="implement all_paths")
def test_all_paths_returns_lists_of_nodes() -> None:
    # Each path is a list (a copy), never a shared/aliased reference.
    g = _graph([(1, 2), (2, 3)])
    result = algorithms.all_paths(g, 1, 3, max_depth=3)
    assert result == [[1, 2, 3]]
    assert all(isinstance(p, list) for p in result)


@pytest.mark.xfail(raises=NotImplementedError, reason="implement all_paths")
def test_all_paths_max_depth_one() -> None:
    # Only the single-hop route survives a 1-hop limit.
    g = _graph([(1, 2), (2, 4), (1, 4)])
    paths = {tuple(p) for p in algorithms.all_paths(g, 1, 4, max_depth=1)}
    assert paths == {(1, 4)}


@pytest.mark.xfail(raises=NotImplementedError, reason="implement all_paths")
def test_all_paths_unknown_source_raises() -> None:
    # An unknown node is a programming error -> KeyError, NOT an empty list. (A
    # `if source not in graph: return []` guard would wrongly swallow this.) An
    # unknown *target*, by contrast, is merely unreachable, so it yields [].
    g = _graph([(1, 2), (2, 3)])
    with pytest.raises(KeyError):
        algorithms.all_paths(g, 99, 2)


# --- Exercise 2: bfs_shortest_path ----------------------------------------


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


@pytest.mark.xfail(raises=NotImplementedError, reason="implement bfs_shortest_path")
def test_bfs_shortest_path_direct_edge() -> None:
    g = _graph([(1, 2)])
    assert algorithms.bfs_shortest_path(g, 1, 2) == [1, 2]


@pytest.mark.xfail(raises=NotImplementedError, reason="implement bfs_shortest_path")
def test_bfs_shortest_path_handles_cycles() -> None:
    # The follow-loop 1->2->3->1 must not trap BFS (a missing `visited` set
    # would spin forever). 3->4 is only reachable by going around the loop.
    g = _graph([(1, 2), (2, 3), (3, 1), (2, 4)])
    assert algorithms.bfs_shortest_path(g, 1, 4) == [1, 2, 4]
    assert algorithms.bfs_shortest_path(g, 3, 4) == [3, 1, 2, 4]


@pytest.mark.xfail(raises=NotImplementedError, reason="implement bfs_shortest_path")
def test_bfs_shortest_path_picks_fewest_hops() -> None:
    # Two equally short routes (1->2->4 and 1->3->4). Either is correct, so
    # assert the hop count and endpoints rather than one specific route.
    g = _graph([(1, 2), (1, 3), (2, 4), (3, 4)])
    path = algorithms.bfs_shortest_path(g, 1, 4)
    assert path is not None
    assert path[0] == 1 and path[-1] == 4
    assert len(path) == 3


@pytest.mark.xfail(raises=NotImplementedError, reason="implement bfs_shortest_path")
def test_bfs_shortest_path_unknown_source_raises() -> None:
    # Unknown source is an error (KeyError); an unknown target is merely
    # unreachable (None, see test_bfs_shortest_path_unreachable).
    g = _graph([(1, 2), (2, 3)])
    with pytest.raises(KeyError):
        algorithms.bfs_shortest_path(g, 99, 2)


# --- Exercise 3: degrees_of_separation ------------------------------------


@pytest.mark.xfail(raises=NotImplementedError, reason="implement degrees_of_separation")
def test_degrees_of_separation() -> None:
    g = _graph([(1, 2), (2, 3), (3, 4), (1, 5), (5, 4)])
    assert algorithms.degrees_of_separation(g, 1, 4) == 2
    assert algorithms.degrees_of_separation(g, 1, 1) == 0
    assert algorithms.degrees_of_separation(g, 4, 1) is None


@pytest.mark.xfail(raises=NotImplementedError, reason="implement degrees_of_separation")
def test_degrees_of_separation_counts_hops_not_nodes() -> None:
    # A direct follow is 1 degree; the far end of a 3-edge chain is 3.
    g = _graph([(1, 2), (2, 3), (3, 4)])
    assert algorithms.degrees_of_separation(g, 1, 2) == 1
    assert algorithms.degrees_of_separation(g, 1, 4) == 3


@pytest.mark.xfail(raises=NotImplementedError, reason="implement degrees_of_separation")
def test_degrees_of_separation_handles_cycles() -> None:
    # The follow-loop 1->2->3->1 must not cause an infinite search.
    g = _graph([(1, 2), (2, 3), (3, 1), (2, 4)])
    assert algorithms.degrees_of_separation(g, 1, 4) == 2
    assert algorithms.degrees_of_separation(g, 3, 4) == 3


@pytest.mark.xfail(raises=NotImplementedError, reason="implement degrees_of_separation")
def test_degrees_of_separation_unknown_source_raises() -> None:
    # Unknown source is an error (KeyError); an unknown target is unreachable (None).
    g = _graph([(1, 2), (2, 3)])
    with pytest.raises(KeyError):
        algorithms.degrees_of_separation(g, 99, 2)


# --- Exercise 4: reachable_within -----------------------------------------


@pytest.mark.xfail(raises=NotImplementedError, reason="implement reachable_within")
def test_reachable_within() -> None:
    g = _graph([(1, 2), (1, 3), (2, 4), (2, 5), (3, 4)])
    assert algorithms.reachable_within(g, 1, 1) == {1: 0, 2: 1, 3: 1}
    assert algorithms.reachable_within(g, 1, 2) == {1: 0, 2: 1, 3: 1, 4: 2, 5: 2}


@pytest.mark.xfail(raises=NotImplementedError, reason="implement reachable_within")
def test_reachable_within_depth_zero() -> None:
    # Depth 0 reaches only the source itself.
    g = _graph([(1, 2), (2, 3)])
    assert algorithms.reachable_within(g, 1, 0) == {1: 0}


@pytest.mark.xfail(raises=NotImplementedError, reason="implement reachable_within")
def test_reachable_within_records_shortest_distance() -> None:
    # Node 2 is reachable directly (1->2, dist 1) and via 3 (1->3->2, dist 2).
    # The recorded distance must be the smaller one.
    g = _graph([(1, 2), (1, 3), (3, 2)])
    assert algorithms.reachable_within(g, 1, 2) == {1: 0, 2: 1, 3: 1}


@pytest.mark.xfail(raises=NotImplementedError, reason="implement reachable_within")
def test_reachable_within_handles_cycles() -> None:
    # The follow-loop 1->2->3->1 returns to the source; the BFS must not
    # re-expand already-seen nodes or it would loop / mis-record distances.
    g = _graph([(1, 2), (2, 3), (3, 1)])
    assert algorithms.reachable_within(g, 1, 5) == {1: 0, 2: 1, 3: 2}


@pytest.mark.xfail(raises=NotImplementedError, reason="implement reachable_within")
def test_reachable_within_sink_source() -> None:
    # A source that follows nobody reaches only itself.
    g = _graph([(2, 3)], isolated=[1])
    assert algorithms.reachable_within(g, 1, 3) == {1: 0}


@pytest.mark.xfail(raises=NotImplementedError, reason="implement reachable_within")
def test_reachable_within_unknown_source_raises() -> None:
    # An unknown source is a programming error, not an empty result.
    g = _graph([(1, 2), (2, 3)])
    with pytest.raises(KeyError):
        algorithms.reachable_within(g, 99, 2)


# --- Exercise 5: common_neighbors -----------------------------------------


@pytest.mark.xfail(raises=NotImplementedError, reason="implement common_neighbors")
def test_common_neighbors() -> None:
    g = _graph([(1, 2), (1, 3), (1, 5), (4, 2), (4, 3), (4, 6)])
    assert algorithms.common_neighbors(g, 1, 4) == {2, 3}


@pytest.mark.xfail(raises=NotImplementedError, reason="implement common_neighbors")
def test_common_neighbors_disjoint_is_empty() -> None:
    # No shared follows -> empty set, not an error.
    g = _graph([(1, 2), (3, 4)])
    assert algorithms.common_neighbors(g, 1, 3) == set()


@pytest.mark.xfail(raises=NotImplementedError, reason="implement common_neighbors")
def test_common_neighbors_unknown_node_raises() -> None:
    # Either argument being unknown is an error (not an empty intersection).
    g = _graph([(1, 2), (2, 3)])
    with pytest.raises(KeyError):
        algorithms.common_neighbors(g, 1, 99)
    with pytest.raises(KeyError):
        algorithms.common_neighbors(g, 99, 1)


# --- Exercise 6: jaccard_similarity ---------------------------------------


@pytest.mark.xfail(raises=NotImplementedError, reason="implement jaccard_similarity")
def test_jaccard_similarity() -> None:
    g = _graph([(1, 2), (1, 3), (1, 5), (4, 2), (4, 3), (4, 6)], isolated=[7, 8])
    # intersection {2,3} (size 2), union {2,3,5,6} (size 4)
    assert algorithms.jaccard_similarity(g, 1, 4) == 0.5
    # neither follows anyone -> defined as 0.0
    assert algorithms.jaccard_similarity(g, 7, 8) == 0.0


@pytest.mark.xfail(raises=NotImplementedError, reason="implement jaccard_similarity")
def test_jaccard_similarity_identical_follows() -> None:
    # Both follow exactly {2, 3} -> perfect similarity.
    g = _graph([(1, 2), (1, 3), (4, 2), (4, 3)])
    assert algorithms.jaccard_similarity(g, 1, 4) == 1.0


@pytest.mark.xfail(raises=NotImplementedError, reason="implement jaccard_similarity")
def test_jaccard_similarity_disjoint_follows() -> None:
    # Both follow someone, but share nobody -> 0.0 (union is non-empty).
    g = _graph([(1, 2), (4, 3)])
    assert algorithms.jaccard_similarity(g, 1, 4) == 0.0


@pytest.mark.xfail(raises=NotImplementedError, reason="implement jaccard_similarity")
def test_jaccard_similarity_unknown_node_raises() -> None:
    # An unknown node is an error, distinct from the "follows nobody" -> 0.0 case.
    g = _graph([(1, 2), (2, 3)])
    with pytest.raises(KeyError):
        algorithms.jaccard_similarity(g, 1, 99)
    with pytest.raises(KeyError):
        algorithms.jaccard_similarity(g, 99, 1)


# --- Exercise 7: recommend_users ------------------------------------------


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


@pytest.mark.xfail(raises=NotImplementedError, reason="implement recommend_users")
def test_recommend_users_respects_limit() -> None:
    # 1 follows 2; 2 follows 3, 4, 5 -> three candidates, each score 1.
    g = _graph([(1, 2), (2, 3), (2, 4), (2, 5)])
    recs = algorithms.recommend_users(g, 1, limit=2)
    assert len(recs) == 2
    assert all(score == 1 for _, score in recs)
    assert {uid for uid, _ in recs}.issubset({3, 4, 5})


@pytest.mark.xfail(raises=NotImplementedError, reason="implement recommend_users")
def test_recommend_users_with_no_follows() -> None:
    # A user who follows nobody has no friends-of-friends to recommend.
    g = _graph([(2, 3)], isolated=[1])
    assert algorithms.recommend_users(g, 1) == []


@pytest.mark.xfail(raises=NotImplementedError, reason="implement recommend_users")
def test_recommend_users_excludes_already_followed_friend_of_friend() -> None:
    # 1 follows {2, 3}. Walking friends-of-friends reaches 3 again (2 follows 3)
    # and 4 (new). 3 must be dropped because 1 already follows them; only 4 is
    # a real recommendation.
    g = _graph([(1, 2), (1, 3), (2, 3), (2, 4)])
    recs = algorithms.recommend_users(g, 1)
    assert recs == [(4, 1)]


@pytest.mark.xfail(raises=NotImplementedError, reason="implement recommend_users")
def test_recommend_users_unknown_user_raises() -> None:
    g = _graph([(1, 2), (2, 3)])
    with pytest.raises(KeyError):
        algorithms.recommend_users(g, 99)


# --- Exercise 8: connected_components -------------------------------------


@pytest.mark.xfail(raises=NotImplementedError, reason="implement connected_components")
def test_connected_components() -> None:
    g = _graph([(1, 2), (2, 3), (3, 4), (1, 5), (5, 4), (10, 11)], isolated=[20])
    components = {frozenset(c) for c in algorithms.connected_components(g)}
    assert components == {
        frozenset({1, 2, 3, 4, 5}),
        frozenset({10, 11}),
        frozenset({20}),
    }


@pytest.mark.xfail(raises=NotImplementedError, reason="implement connected_components")
def test_connected_components_empty_graph() -> None:
    assert algorithms.connected_components(DirectedGraph()) == []


@pytest.mark.xfail(raises=NotImplementedError, reason="implement connected_components")
def test_connected_components_single_component() -> None:
    # A directed chain is still one component under undirected reachability.
    g = _graph([(1, 2), (2, 3)])
    components = [frozenset(c) for c in algorithms.connected_components(g)]
    assert components == [frozenset({1, 2, 3})]


# --- Exercise 9: local_clustering_coefficient -----------------------------


@pytest.mark.xfail(raises=NotImplementedError, reason="implement local_clustering_coefficient")
def test_local_clustering_coefficient() -> None:
    # Undirected neighbors of 1 are {2,3,4}; only the 2-3 edge exists among them.
    g = _graph([(1, 2), (1, 3), (2, 3), (1, 4)])
    assert algorithms.local_clustering_coefficient(g, 1) == pytest.approx(1 / 3)
    # node 4 has a single neighbor -> 0.0
    assert algorithms.local_clustering_coefficient(g, 4) == 0.0


@pytest.mark.xfail(raises=NotImplementedError, reason="implement local_clustering_coefficient")
def test_local_clustering_coefficient_full_clique() -> None:
    # 1's neighbors {2, 3} follow each other -> fully connected -> 1.0.
    g = _graph([(1, 2), (1, 3), (2, 3)])
    assert algorithms.local_clustering_coefficient(g, 1) == 1.0


@pytest.mark.xfail(raises=NotImplementedError, reason="implement local_clustering_coefficient")
def test_local_clustering_coefficient_no_links_among_neighbors() -> None:
    # Two neighbors with no edge between them -> 0.0.
    g = _graph([(1, 2), (1, 3)])
    assert algorithms.local_clustering_coefficient(g, 1) == 0.0


@pytest.mark.xfail(raises=NotImplementedError, reason="implement local_clustering_coefficient")
def test_local_clustering_coefficient_isolated_node() -> None:
    # Zero neighbors -> 0.0 (and no division by zero).
    g = _graph([(2, 3)], isolated=[1])
    assert algorithms.local_clustering_coefficient(g, 1) == 0.0


@pytest.mark.xfail(raises=NotImplementedError, reason="implement local_clustering_coefficient")
def test_local_clustering_coefficient_uses_undirected_neighbors() -> None:
    # Node 1's neighborhood only emerges under the undirected view: 2 is a
    # *follower* (2->1) and 3 is a *followee* (1->3), and the link between them
    # (3->2) points "backwards". An implementation that uses raw successors
    # would see one neighbor and return 0.0 instead of the correct 1.0.
    g = _graph([(2, 1), (1, 3), (3, 2)])
    assert algorithms.local_clustering_coefficient(g, 1) == 1.0


@pytest.mark.xfail(raises=NotImplementedError, reason="implement local_clustering_coefficient")
def test_local_clustering_coefficient_unknown_node_raises() -> None:
    # Fewer than 2 neighbors is a valid 0.0; a node that doesn't exist is an error.
    g = _graph([(1, 2), (2, 3)])
    with pytest.raises(KeyError):
        algorithms.local_clustering_coefficient(g, 99)


# --- Exercise 10: pagerank ------------------------------------------------


@pytest.mark.xfail(raises=NotImplementedError, reason="implement pagerank")
def test_pagerank() -> None:
    # Everyone follows node 1, so node 1 should rank highest.
    g = _graph([(2, 1), (3, 1), (4, 1), (1, 2)])
    ranks = algorithms.pagerank(g)
    assert set(ranks.keys()) == {1, 2, 3, 4}
    assert sum(ranks.values()) == pytest.approx(1.0, abs=1e-3)
    assert max(ranks, key=ranks.get) == 1


@pytest.mark.xfail(raises=NotImplementedError, reason="implement pagerank")
def test_pagerank_symmetric_pair() -> None:
    # A mutual follow is perfectly symmetric -> both ranks equal, ~0.5 each.
    g = _graph([(1, 2), (2, 1)])
    ranks = algorithms.pagerank(g)
    assert ranks[1] == pytest.approx(ranks[2])
    assert ranks[1] == pytest.approx(0.5, abs=1e-3)


@pytest.mark.xfail(raises=NotImplementedError, reason="implement pagerank")
def test_pagerank_handles_dangling_node() -> None:
    # Node 2 follows no one (a "dangling" node). Its rank must be redistributed
    # rather than leaking out, so the scores still sum to ~1.0.
    g = _graph([(1, 2)])
    ranks = algorithms.pagerank(g)
    assert set(ranks.keys()) == {1, 2}
    assert sum(ranks.values()) == pytest.approx(1.0, abs=1e-3)


@pytest.mark.xfail(raises=NotImplementedError, reason="implement pagerank")
def test_pagerank_edgeless_graph_is_uniform() -> None:
    # With no edges every node is dangling. Rank must not leak: each of the 4
    # nodes ends up with an equal 1/4 share.
    g = _graph([], isolated=[1, 2, 3, 4])
    ranks = algorithms.pagerank(g)
    assert sum(ranks.values()) == pytest.approx(1.0, abs=1e-3)
    for score in ranks.values():
        assert score == pytest.approx(0.25, abs=1e-3)


# --- Exercise 11: detect_communities --------------------------------------


@pytest.mark.xfail(raises=NotImplementedError, reason="implement detect_communities")
def test_detect_communities() -> None:
    # Two separate cliques: {1,2,3} and {4,5}.
    g = _graph([(1, 2), (2, 1), (2, 3), (3, 2), (1, 3), (3, 1), (4, 5), (5, 4)])
    labels = algorithms.detect_communities(g)
    assert labels[1] == labels[2] == labels[3]
    assert labels[4] == labels[5]
    assert labels[1] != labels[4]
    assert len(set(labels.values())) == 2


@pytest.mark.xfail(raises=NotImplementedError, reason="implement detect_communities")
def test_detect_communities_single_clique() -> None:
    # One fully-connected group collapses to a single community.
    g = _graph([(1, 2), (2, 1), (2, 3), (3, 2), (1, 3), (3, 1)])
    labels = algorithms.detect_communities(g)
    assert len(set(labels.values())) == 1


@pytest.mark.xfail(raises=NotImplementedError, reason="implement detect_communities")
def test_detect_communities_labels_renumbered_from_zero() -> None:
    # Two separate mutual-follow pairs; ids must be tidied to 0, 1, ...
    g = _graph([(1, 2), (2, 1), (4, 5), (5, 4)])
    labels = algorithms.detect_communities(g)
    assert set(labels.values()) == {0, 1}


@pytest.mark.xfail(raises=NotImplementedError, reason="implement detect_communities")
def test_detect_communities_isolated_node_is_its_own_community() -> None:
    # A node with no neighbors keeps its own label (and must not crash on the
    # empty-neighbor case): the mutual pair {1, 2} is one community, 3 another.
    g = _graph([(1, 2), (2, 1)], isolated=[3])
    labels = algorithms.detect_communities(g)
    assert labels[1] == labels[2]
    assert labels[3] != labels[1]
    assert len(set(labels.values())) == 2
