"""Build an in-memory graph from the database.

This is the bridge between the persistent data (the `follows` table) and the
in-memory `DirectedGraph` the algorithms run on. It is fully implemented — the
interesting work is in `algorithms.py`.

Edge direction convention (important for every algorithm!):

    an edge  follower_id -> following_id  means "follower follows following".

So for a node `u`:
    graph.successors(u)   == the users u follows
    graph.predecessors(u) == the users who follow u (u's followers)
"""

from sqlmodel import Session, select

from app.graph.graph import DirectedGraph
from app.models import Follow, User


def build_follow_graph(session: Session) -> DirectedGraph:
    """Load every user as a node and every follow as a directed edge.

    Users with no connections are still added as isolated nodes so algorithms
    that iterate over `graph.nodes` see the whole network.
    """
    graph = DirectedGraph()

    # Add all users first so isolated accounts are represented.
    for user_id in session.exec(select(User.id)).all():
        graph.add_node(user_id)

    # Add an edge for each follow relationship.
    for follow in session.exec(select(Follow)).all():
        graph.add_edge(follow.follower_id, follow.following_id)

    return graph


# NOTE for later: building the graph on every request is fine for a class-sized
# dataset. If the network grows, this is the place to add caching (build once,
# invalidate when a follow/unfollow happens) — a nice optional exercise.
