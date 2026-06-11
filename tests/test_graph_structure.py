"""Unit tests for the DirectedGraph data structure — STUDENT EXERCISE 0.

The methods of ``DirectedGraph`` (app/graph/graph.py) start out as stubs that
raise ``NotImplementedError``, so this whole file fails at first. That's the
point: it is your spec and your progress bar.

WORKFLOW:
  Implement the steps in order (each class below names its step) and run just
  that step's tests, e.g.:

      pytest tests/test_graph_structure.py -k Step01

  Each step's tests use only the methods from that step and the steps before
  it, so finishing step N turns its tests green without touching step N+1.
  When every test in this file passes, the graph is complete — the builder,
  the algorithm exercises, and the API endpoints can all use it.

Suggested order (matches the stubs in graph.py):

  Step 01  add_node, has_node
  Step 02  add_edge, has_edge
  Step 03  nodes, number_of_nodes  (+ the provided `in` / `len` dunders)
  Step 04  successors, predecessors (and the `neighbors` alias)
  Step 05  out_degree, in_degree
  Step 06  edges, number_of_edges
  Step 07  remove_edge
  Step 08  remove_node
  Step 09  to_undirected
  Step 10  the full-scenario integration test
"""

import pytest

from app.graph.graph import DirectedGraph


# ---------------------------------------------------------------------------
# Step 01 — add_node / has_node
# ---------------------------------------------------------------------------
class TestStep01AddNode:
    """Needs: add_node, has_node."""

    def test_new_graph_has_no_nodes(self) -> None:
        g = DirectedGraph()
        assert not g.has_node(1)

    def test_added_node_is_present(self) -> None:
        g = DirectedGraph()
        g.add_node(1)
        assert g.has_node(1)

    def test_other_nodes_are_still_absent(self) -> None:
        g = DirectedGraph()
        g.add_node(1)
        assert not g.has_node(2)

    def test_adding_twice_is_a_quiet_no_op(self) -> None:
        g = DirectedGraph()
        g.add_node(1)
        g.add_node(1)  # must not raise (the duplicate-count check is Step 03)
        assert g.has_node(1)

    def test_any_hashable_value_can_be_a_node(self) -> None:
        g = DirectedGraph()
        g.add_node("alice")
        g.add_node((1, 2))
        assert g.has_node("alice")
        assert g.has_node((1, 2))

    def test_in_operator_delegates_to_has_node(self) -> None:
        # `node in graph` is provided in graph.py — it calls your has_node.
        g = DirectedGraph()
        g.add_node(1)
        assert 1 in g
        assert 5 not in g


# ---------------------------------------------------------------------------
# Step 02 — add_edge / has_edge
# ---------------------------------------------------------------------------
class TestStep02AddEdge:
    """Needs: add_edge, has_edge (+ Step 01)."""

    def test_added_edge_is_present(self) -> None:
        g = DirectedGraph()
        g.add_edge(1, 2)
        assert g.has_edge(1, 2)

    def test_edges_are_directed(self) -> None:
        g = DirectedGraph()
        g.add_edge(1, 2)
        assert not g.has_edge(2, 1)

    def test_add_edge_creates_missing_endpoints(self) -> None:
        g = DirectedGraph()
        g.add_edge(1, 2)
        assert g.has_node(1)
        assert g.has_node(2)

    def test_add_edge_keeps_existing_nodes(self) -> None:
        g = DirectedGraph()
        g.add_node(1)
        g.add_edge(1, 2)  # 1 already exists; must not lose anything
        assert g.has_edge(1, 2)

    def test_duplicate_edge_is_a_quiet_no_op(self) -> None:
        g = DirectedGraph()
        g.add_edge(1, 2)
        g.add_edge(1, 2)  # must not raise (the count check is Step 06)
        assert g.has_edge(1, 2)

    def test_has_edge_is_false_for_unknown_nodes(self) -> None:
        g = DirectedGraph()
        assert not g.has_edge(7, 8)  # must not raise

    def test_self_loop_is_allowed(self) -> None:
        g = DirectedGraph()
        g.add_edge(1, 1)
        assert g.has_edge(1, 1)


# ---------------------------------------------------------------------------
# Step 03 — nodes / number_of_nodes (and the provided dunders)
# ---------------------------------------------------------------------------
class TestStep03Nodes:
    """Needs: nodes, number_of_nodes (+ Steps 01–02)."""

    def test_empty_graph(self) -> None:
        g = DirectedGraph()
        assert g.nodes == set()
        assert g.number_of_nodes() == 0

    def test_nodes_returns_every_node(self) -> None:
        g = DirectedGraph()
        g.add_node(1)
        g.add_edge(2, 3)
        assert g.nodes == {1, 2, 3}
        assert g.number_of_nodes() == 3

    def test_adding_a_node_twice_does_not_duplicate(self) -> None:
        g = DirectedGraph()
        g.add_node(1)
        g.add_node(1)
        assert g.number_of_nodes() == 1

    def test_nodes_returns_a_copy(self) -> None:
        g = DirectedGraph()
        g.add_node(1)
        g.nodes.add(99)  # mutating the returned set must not corrupt the graph
        assert g.nodes == {1}

    def test_len_delegates_to_number_of_nodes(self) -> None:
        # `len(graph)` is provided in graph.py — it calls your number_of_nodes.
        g = DirectedGraph()
        g.add_edge(1, 2)
        assert len(g) == 2


# ---------------------------------------------------------------------------
# Step 04 — successors / predecessors / neighbors
# ---------------------------------------------------------------------------
class TestStep04SuccessorsPredecessors:
    """Needs: successors, predecessors (+ Steps 01–02)."""

    def test_successors_are_who_the_node_points_to(self) -> None:
        g = DirectedGraph()
        g.add_edge(1, 2)
        g.add_edge(1, 3)
        assert g.successors(1) == {2, 3}

    def test_predecessors_are_who_points_to_the_node(self) -> None:
        g = DirectedGraph()
        g.add_edge(1, 2)
        g.add_edge(3, 2)
        assert g.predecessors(2) == {1, 3}

    def test_direction_is_respected(self) -> None:
        g = DirectedGraph()
        g.add_edge(1, 2)
        assert g.successors(2) == set()
        assert g.predecessors(1) == set()

    def test_isolated_node_has_empty_sets(self) -> None:
        g = DirectedGraph()
        g.add_node(1)
        assert g.successors(1) == set()
        assert g.predecessors(1) == set()

    def test_missing_node_raises_key_error(self) -> None:
        g = DirectedGraph()
        with pytest.raises(KeyError):
            g.successors(42)
        with pytest.raises(KeyError):
            g.predecessors(42)

    def test_returned_sets_are_copies(self) -> None:
        g = DirectedGraph()
        g.add_edge(1, 2)
        g.successors(1).add(99)
        g.predecessors(2).add(99)
        assert g.successors(1) == {2}
        assert g.predecessors(2) == {1}

    def test_neighbors_is_an_alias_for_successors(self) -> None:
        g = DirectedGraph()
        g.add_edge(1, 2)
        g.add_edge(3, 1)
        assert g.neighbors(1) == g.successors(1) == {2}


# ---------------------------------------------------------------------------
# Step 05 — out_degree / in_degree
# ---------------------------------------------------------------------------
class TestStep05Degrees:
    """Needs: out_degree, in_degree (+ Steps 01–02)."""

    def test_degrees_count_each_direction(self) -> None:
        g = DirectedGraph()
        g.add_edge(1, 2)
        g.add_edge(1, 3)
        g.add_edge(4, 1)
        assert g.out_degree(1) == 2
        assert g.in_degree(1) == 1

    def test_isolated_node_has_zero_degrees(self) -> None:
        g = DirectedGraph()
        g.add_node(1)
        assert g.out_degree(1) == 0
        assert g.in_degree(1) == 0

    def test_missing_node_raises_key_error(self) -> None:
        g = DirectedGraph()
        with pytest.raises(KeyError):
            g.out_degree(42)
        with pytest.raises(KeyError):
            g.in_degree(42)


# ---------------------------------------------------------------------------
# Step 06 — edges / number_of_edges
# ---------------------------------------------------------------------------
class TestStep06Edges:
    """Needs: edges, number_of_edges (+ Steps 01–02)."""

    def test_empty_graph_has_no_edges(self) -> None:
        g = DirectedGraph()
        assert list(g.edges()) == []
        assert g.number_of_edges() == 0

    def test_every_edge_appears_exactly_once(self) -> None:
        g = DirectedGraph()
        g.add_edge(1, 2)
        g.add_edge(2, 1)
        g.add_edge(2, 3)
        listed = list(g.edges())
        assert len(listed) == 3
        assert set(listed) == {(1, 2), (2, 1), (2, 3)}
        assert g.number_of_edges() == 3

    def test_duplicate_add_edge_is_not_double_counted(self) -> None:
        g = DirectedGraph()
        g.add_edge(1, 2)
        g.add_edge(1, 2)
        assert g.number_of_edges() == 1

    def test_isolated_nodes_contribute_no_edges(self) -> None:
        g = DirectedGraph()
        g.add_node(1)
        g.add_edge(2, 3)
        assert set(g.edges()) == {(2, 3)}

    def test_self_loop_counts_once(self) -> None:
        g = DirectedGraph()
        g.add_edge(1, 1)
        assert set(g.edges()) == {(1, 1)}
        assert g.number_of_edges() == 1


# ---------------------------------------------------------------------------
# Step 07 — remove_edge
# ---------------------------------------------------------------------------
class TestStep07RemoveEdge:
    """Needs: remove_edge (+ Steps 01–06)."""

    def test_removed_edge_is_gone(self) -> None:
        g = DirectedGraph()
        g.add_edge(1, 2)
        g.remove_edge(1, 2)
        assert not g.has_edge(1, 2)

    def test_both_directions_are_updated(self) -> None:
        # The bug this catches: removing from the successor side but
        # forgetting the predecessor side (or vice versa).
        g = DirectedGraph()
        g.add_edge(1, 2)
        g.remove_edge(1, 2)
        assert g.successors(1) == set()
        assert g.predecessors(2) == set()

    def test_reverse_edge_survives(self) -> None:
        g = DirectedGraph()
        g.add_edge(1, 2)
        g.add_edge(2, 1)
        g.remove_edge(1, 2)
        assert g.has_edge(2, 1)

    def test_nodes_are_kept(self) -> None:
        g = DirectedGraph()
        g.add_edge(1, 2)
        g.remove_edge(1, 2)
        assert g.has_node(1)
        assert g.has_node(2)

    def test_other_edges_are_untouched(self) -> None:
        g = DirectedGraph()
        g.add_edge(1, 2)
        g.add_edge(1, 3)
        g.remove_edge(1, 2)
        assert g.successors(1) == {3}

    def test_removing_a_missing_edge_is_a_quiet_no_op(self) -> None:
        g = DirectedGraph()
        g.add_node(1)
        g.remove_edge(1, 2)  # edge never existed
        g.remove_edge(7, 8)  # neither node exists
        assert g.number_of_edges() == 0


# ---------------------------------------------------------------------------
# Step 08 — remove_node
# ---------------------------------------------------------------------------
class TestStep08RemoveNode:
    """Needs: remove_node (+ Steps 01–06)."""

    def test_removed_node_is_gone(self) -> None:
        g = DirectedGraph()
        g.add_node(1)
        g.remove_node(1)
        assert not g.has_node(1)
        assert g.number_of_nodes() == 0

    def test_outgoing_edges_are_cleaned_up(self) -> None:
        g = DirectedGraph()
        g.add_edge(1, 2)
        g.remove_node(1)
        assert g.predecessors(2) == set()  # no dangling reference to 1

    def test_incoming_edges_are_cleaned_up(self) -> None:
        g = DirectedGraph()
        g.add_edge(1, 2)
        g.remove_node(2)
        assert g.successors(1) == set()  # no dangling reference to 2

    def test_unrelated_edges_survive(self) -> None:
        g = DirectedGraph()
        g.add_edge(1, 2)
        g.add_edge(3, 4)
        g.remove_node(1)
        assert g.has_edge(3, 4)
        assert g.number_of_edges() == 1

    def test_removing_a_missing_node_is_a_quiet_no_op(self) -> None:
        g = DirectedGraph()
        g.remove_node(42)  # must not raise
        assert g.number_of_nodes() == 0

    def test_graph_stays_consistent_after_removal(self) -> None:
        # A hub with edges in both directions; removing it must leave no trace.
        g = DirectedGraph()
        g.add_edge(1, 9)
        g.add_edge(2, 9)
        g.add_edge(9, 3)
        g.remove_node(9)
        assert g.nodes == {1, 2, 3}
        assert g.number_of_edges() == 0
        for node in (1, 2, 3):
            assert g.successors(node) == set()
            assert g.predecessors(node) == set()


# ---------------------------------------------------------------------------
# Step 09 — to_undirected
# ---------------------------------------------------------------------------
class TestStep09ToUndirected:
    """Needs: to_undirected (+ Steps 01–06)."""

    def test_returns_a_directed_graph(self) -> None:
        g = DirectedGraph()
        g.add_edge(1, 2)
        assert isinstance(g.to_undirected(), DirectedGraph)

    def test_every_edge_points_both_ways(self) -> None:
        g = DirectedGraph()
        g.add_edge(1, 2)
        u = g.to_undirected()
        assert u.has_edge(1, 2)
        assert u.has_edge(2, 1)

    def test_successors_equal_predecessors_everywhere(self) -> None:
        g = DirectedGraph()
        g.add_edge(1, 2)
        g.add_edge(2, 3)
        g.add_edge(4, 2)
        u = g.to_undirected()
        for node in u.nodes:
            assert u.successors(node) == u.predecessors(node)

    def test_isolated_nodes_are_preserved(self) -> None:
        g = DirectedGraph()
        g.add_node(7)
        g.add_edge(1, 2)
        assert g.to_undirected().nodes == {1, 2, 7}

    def test_mutual_follow_does_not_duplicate(self) -> None:
        g = DirectedGraph()
        g.add_edge(1, 2)
        g.add_edge(2, 1)
        u = g.to_undirected()
        assert u.number_of_edges() == 2  # exactly (1,2) and (2,1)

    def test_original_graph_is_not_modified(self) -> None:
        g = DirectedGraph()
        g.add_edge(1, 2)
        u = g.to_undirected()
        u.add_edge(5, 6)
        assert not g.has_edge(2, 1)  # original is still directed
        assert not g.has_node(5)  # and didn't gain the copy's new edge


# ---------------------------------------------------------------------------
# Step 10 — the whole structure working together
# ---------------------------------------------------------------------------
class TestStep10FullScenario:
    """Uses every method. When this passes, the graph is ready for the
    builder, the algorithm exercises, and the API endpoints."""

    def test_small_social_network_end_to_end(self) -> None:
        g = DirectedGraph()

        # alice(1) and bob(2) follow each other; both follow the hub celeb(3);
        # carol(4) follows alice; lurker(5) has an account but no follows.
        for u, v in [(1, 2), (2, 1), (1, 3), (2, 3), (4, 1)]:
            g.add_edge(u, v)
        g.add_node(5)

        assert len(g) == 5
        assert g.number_of_edges() == 5
        assert g.successors(1) == {2, 3}
        assert g.predecessors(1) == {2, 4}
        assert g.in_degree(3) == 2 and g.out_degree(3) == 0
        assert set(g.edges()) == {(1, 2), (2, 1), (1, 3), (2, 3), (4, 1)}

        # celeb deletes their account; carol unfollows alice
        g.remove_node(3)
        g.remove_edge(4, 1)
        assert g.nodes == {1, 2, 4, 5}
        assert g.number_of_edges() == 2
        assert g.successors(1) == {2}
        assert g.predecessors(1) == {2}

        # the undirected view still sees the mutual pair and the loners
        u = g.to_undirected()
        assert u.neighbors(1) == {2}
        assert u.neighbors(4) == set()
        assert u.neighbors(5) == set()
