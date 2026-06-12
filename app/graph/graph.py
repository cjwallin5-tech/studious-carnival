"""A minimal in-memory directed graph — STUDENT EXERCISE 0.

Before the algorithms in ``algorithms.py`` can run, the data structure they
operate on has to exist. Every method below is a stub that raises
``NotImplementedError``; your job is to implement them, guided by the tests in
``tests/test_graph_structure.py``. Work through the steps in order and run one
step's tests at a time:

    pytest tests/test_graph_structure.py -k Step01

When the whole file passes, the graph is complete: the builder, the algorithm
exercises, and the ``/graph`` API endpoints can all use it. (Until then, every
graph endpoint returns 501 — the structure is the foundation.)

Representation: an **adjacency list** built from two dictionaries.

    self._out[u] -> set of nodes that u points to   (u's successors / who u follows)
    self._in[u]  -> set of nodes that point to u     (u's predecessors / u's followers)

Keeping both directions costs a little extra memory but makes "who follows me?"
(predecessors) just as fast as "who do I follow?" (successors). Every edge is
stored once in each dictionary, and **every method that changes the graph must
keep the two dictionaries in sync** — most of the bugs the tests catch are
one-sided updates. A node always has an entry in BOTH dicts (an empty set if it
has no edges on that side).

Nodes can be any hashable value; in this project a node is a user's integer id.
"""

from __future__ import annotations

from collections.abc import Hashable, Iterator

Node = Hashable


class DirectedGraph:
    def __init__(self) -> None:
        # node -> set of successors (outgoing edges)
        self._out: dict[Node, set[Node]] = {}
        # node -> set of predecessors (incoming edges)
        self._in: dict[Node, set[Node]] = {}

    # ----- mutation -------------------------------------------------------

    def add_node(self, node: Node) -> None:
        """Add a node. Must be a quiet no-op if it already exists.

        Sketch: give the node an empty entry in BOTH ``self._out`` and
        ``self._in`` — but don't overwrite an entry that's already there
        (``dict.setdefault`` does exactly this).

        Step 01 · tested by TestStep01AddNode.
        """
        self._out.setdefault(node, set())
        self._in.setdefault(node, set())

    def add_edge(self, u: Node, v: Node) -> None:
        """Add a directed edge u -> v, creating the endpoints if needed.

        Sketch: make sure both nodes exist (reuse ``add_node``), then record
        the edge on both sides: v into u's successor set, u into v's
        predecessor set. Adding the same edge twice must be a quiet no-op
        (sets give you that for free).

        Step 02 · tested by TestStep02AddEdge.
        """
        self.add_node(u)
        self.add_node(v)
        self._out[u].add(v)
        self._in[v].add(u)

    def remove_edge(self, u: Node, v: Node) -> None:
        """Remove the edge u -> v if it exists (the nodes are kept).

        Must be a quiet no-op when the edge — or either node — doesn't exist.
        Remember to remove the edge from BOTH dictionaries.
        (``set.discard`` is ``remove`` without the KeyError.)

        Step 07 · tested by TestStep07RemoveEdge.
        """
        raise NotImplementedError("Graph step 07: implement remove_edge")

    def remove_node(self, node: Node) -> None:
        """Remove a node and every edge touching it.

        Must be a quiet no-op if the node doesn't exist. The subtle part:
        other nodes' entries still mention this node. For each of the node's
        successors, discard the node from that successor's ``_in`` set; for
        each predecessor, discard it from that predecessor's ``_out`` set.
        Then drop the node's own entries from both dictionaries.

        Step 08 · tested by TestStep08RemoveNode.
        """
        raise NotImplementedError("Graph step 08: implement remove_node")

    # ----- queries --------------------------------------------------------

    def has_node(self, node: Node) -> bool:
        """Return True if the node is in the graph. Never raises.

        Step 01 · tested by TestStep01AddNode.
        """
        return node in self._out

    def has_edge(self, u: Node, v: Node) -> bool:
        """Return True if the edge u -> v exists. Never raises — unknown
        nodes simply mean the edge isn't there.

        Step 02 · tested by TestStep02AddEdge.
        """
        return v in self._out.get(u, set())

    def successors(self, node: Node) -> set[Node]:
        """Nodes this node points to (who ``node`` follows).

        Raise ``KeyError`` if the node isn't in the graph (the provided
        ``self._require(node)`` helper does this). Return a **copy** of the
        set — callers will mutate what you give them, and that must never
        corrupt the graph.

        Step 04 · tested by TestStep04SuccessorsPredecessors.
        """
        raise NotImplementedError("Graph step 04: implement successors")

    def predecessors(self, node: Node) -> set[Node]:
        """Nodes that point to this node (``node``'s followers).

        Same contract as ``successors``: KeyError for unknown nodes, and
        return a copy.

        Step 04 · tested by TestStep04SuccessorsPredecessors.
        """
        raise NotImplementedError("Graph step 04: implement predecessors")

    # `neighbors` is an alias for successors — handy in undirected contexts
    # (after `to_undirected`, successors == predecessors == "the neighbors").
    # Provided for you: once successors works, so does this.
    neighbors = successors

    def out_degree(self, node: Node) -> int:
        """How many nodes this node points to. KeyError if unknown.

        Step 05 · tested by TestStep05Degrees.
        """
        raise NotImplementedError("Graph step 05: implement out_degree")

    def in_degree(self, node: Node) -> int:
        """How many nodes point to this node. KeyError if unknown.

        Step 05 · tested by TestStep05Degrees.
        """
        raise NotImplementedError("Graph step 05: implement in_degree")

    @property
    def nodes(self) -> set[Node]:
        """The set of all nodes. Return a copy, not the internal dict's keys.

        Step 03 · tested by TestStep03Nodes.
        """
        return set(self._out)

    def edges(self) -> Iterator[tuple[Node, Node]]:
        """Yield every directed edge exactly once as a (source, target) tuple.

        Sketch: for each node u and each v in u's successor set, yield (u, v).
        A generator (``yield``) is the natural fit, but returning a list of
        tuples also passes the tests.

        Step 06 · tested by TestStep06Edges.
        """
        raise NotImplementedError("Graph step 06: implement edges")

    def number_of_nodes(self) -> int:
        """Total node count.

        Step 03 · tested by TestStep03Nodes.
        """
        return len(self._out)

    def number_of_edges(self) -> int:
        """Total directed-edge count (sum of all the successor-set sizes).

        Step 06 · tested by TestStep06Edges.
        """
        raise NotImplementedError("Graph step 06: implement number_of_edges")

    # ----- transforms -----------------------------------------------------

    def to_undirected(self) -> DirectedGraph:
        """Return a NEW graph where every edge points both ways.

        Useful for algorithms that treat a follow as a symmetric connection
        (e.g. connected components, clustering coefficient). On the returned
        graph, ``successors(n)`` and ``predecessors(n)`` are identical, so
        ``neighbors(n)`` gives the full undirected neighborhood.

        Sketch: build a fresh ``DirectedGraph``; copy every node (so isolated
        nodes survive); then for every edge (u, v), add BOTH (u, v) and
        (v, u). The original graph must not be touched.

        Step 09 · tested by TestStep09ToUndirected.
        """
        raise NotImplementedError("Graph step 09: implement to_undirected")

    # ----- helpers (provided) ----------------------------------------------

    def _require(self, node: Node) -> None:
        """Raise KeyError if the node isn't in the graph."""
        if node not in self._out:
            raise KeyError(f"node {node!r} is not in the graph")

    # ----- dunders (provided — they delegate to your methods) ---------------

    def __contains__(self, node: Node) -> bool:
        return self.has_node(node)

    def __len__(self) -> int:
        return self.number_of_nodes()

    def __repr__(self) -> str:
        # Reads the internals directly so repr works even while the
        # counting methods are still unimplemented.
        n_edges = sum(len(targets) for targets in self._out.values())
        return f"<DirectedGraph nodes={len(self._out)} edges={n_edges}>"
