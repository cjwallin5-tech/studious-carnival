"""Graph endpoints.

Each route builds an in-memory follow graph from the database and calls one of
the algorithms in ``app/graph/algorithms.py``. While an algorithm is still a
stub it raises ``NotImplementedError``; a handler in ``app/main.py`` turns that
into an HTTP 501 (Not Implemented) response, so these endpoints "light up" as
students implement the algorithms.
"""

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.graph import algorithms
from app.graph.builder import build_follow_graph
from app.models import User
from app.schemas.user import UserPublic

router = APIRouter(prefix="/graph", tags=["graph"])


# ----- helpers -------------------------------------------------------------


def _require_user(session: SessionDep, user_id: int) -> User:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def _users_by_ids(session: SessionDep, ids: list[int]) -> dict[int, UserPublic]:
    """Fetch the given users in one query and return them keyed by id."""
    if not ids:
        return {}
    rows = session.exec(select(User).where(User.id.in_(ids))).all()
    return {u.id: UserPublic.model_validate(u) for u in rows}


# ----- routes --------------------------------------------------------------


@router.get("/users/{user_id}/recommendations")
def recommendations(
    user_id: int,
    session: SessionDep,
    limit: int = Query(default=10, ge=1, le=100),
) -> list[dict]:
    """People you may know — friends-of-friends ranked by mutual connections.

    Powered by ``algorithms.recommend_users`` (Exercise 6).
    """
    _require_user(session, user_id)
    graph = build_follow_graph(session)
    scored = algorithms.recommend_users(graph, user_id, limit=limit)

    users = _users_by_ids(session, [uid for uid, _ in scored])
    return [{"user": users.get(uid), "score": score} for uid, score in scored if uid in users]


@router.get("/users/{source_id}/path/{target_id}")
def shortest_path(source_id: int, target_id: int, session: SessionDep) -> dict:
    """Shortest follow-path and degrees of separation between two users.

    Powered by ``algorithms.bfs_shortest_path`` (Exercise 1) and
    ``algorithms.degrees_of_separation`` (Exercise 2).
    """
    _require_user(session, source_id)
    _require_user(session, target_id)
    graph = build_follow_graph(session)

    path = algorithms.bfs_shortest_path(graph, source_id, target_id)
    if path is None:
        return {"connected": False, "degrees": None, "path": []}

    users = _users_by_ids(session, path)
    return {
        "connected": True,
        "degrees": len(path) - 1,
        "path": [users.get(uid) for uid in path],
    }


@router.get("/users/{source_id}/degrees/{target_id}")
def degrees(source_id: int, target_id: int, session: SessionDep) -> dict:
    """Degrees of separation between two users (hop count only).

    The path endpoint above derives its hop count from the BFS path, so this
    route exists to exercise ``algorithms.degrees_of_separation`` (Exercise 2)
    on its own.
    """
    _require_user(session, source_id)
    _require_user(session, target_id)
    graph = build_follow_graph(session)

    hops = algorithms.degrees_of_separation(graph, source_id, target_id)
    return {"connected": hops is not None, "degrees": hops}


@router.get("/users/{user_id}/reachable")
def reachable(
    user_id: int,
    session: SessionDep,
    max_depth: int = Query(default=2, ge=1, le=6),
) -> list[dict]:
    """Everyone reachable from a user within ``max_depth`` hops.

    Powered by ``algorithms.reachable_within`` (Exercise 3).
    """
    _require_user(session, user_id)
    graph = build_follow_graph(session)
    distances = algorithms.reachable_within(graph, user_id, max_depth)

    users = _users_by_ids(session, list(distances.keys()))
    return [
        {"user": users.get(uid), "depth": depth}
        for uid, depth in sorted(distances.items(), key=lambda kv: kv[1])
        if uid in users
    ]


@router.get("/users/{user_id}/mutuals/{other_id}")
def mutuals(user_id: int, other_id: int, session: SessionDep) -> list[UserPublic]:
    """Accounts that both users follow.

    Powered by ``algorithms.common_neighbors`` (Exercise 4).
    """
    _require_user(session, user_id)
    _require_user(session, other_id)
    graph = build_follow_graph(session)
    shared = algorithms.common_neighbors(graph, user_id, other_id)

    users = _users_by_ids(session, list(shared))
    return [users[uid] for uid in shared if uid in users]


@router.get("/users/{user_id}/similarity/{other_id}")
def similarity(user_id: int, other_id: int, session: SessionDep) -> dict:
    """Jaccard similarity (0..1) between two users by who they follow.

    Powered by ``algorithms.jaccard_similarity`` (Exercise 5).
    """
    _require_user(session, user_id)
    _require_user(session, other_id)
    graph = build_follow_graph(session)
    return {"similarity": algorithms.jaccard_similarity(graph, user_id, other_id)}


@router.get("/influencers")
def influencers(
    session: SessionDep,
    limit: int = Query(default=10, ge=1, le=100),
) -> list[dict]:
    """Most influential users by PageRank.

    Powered by ``algorithms.pagerank`` (Exercise 9).
    """
    graph = build_follow_graph(session)
    ranks = algorithms.pagerank(graph)

    top = sorted(ranks.items(), key=lambda kv: kv[1], reverse=True)[:limit]
    users = _users_by_ids(session, [uid for uid, _ in top])
    return [{"user": users.get(uid), "score": score} for uid, score in top if uid in users]


@router.get("/users/{user_id}/clustering")
def clustering(user_id: int, session: SessionDep) -> dict:
    """Local clustering coefficient — how interconnected a user's circle is.

    Powered by ``algorithms.local_clustering_coefficient`` (Exercise 8).
    """
    _require_user(session, user_id)
    graph = build_follow_graph(session)
    return {
        "user_id": user_id,
        "clustering_coefficient": algorithms.local_clustering_coefficient(graph, user_id),
    }


@router.get("/communities")
def communities(session: SessionDep) -> list[dict]:
    """Detected communities (clusters of densely connected users).

    Powered by ``algorithms.detect_communities`` (Exercise 10).
    """
    graph = build_follow_graph(session)
    labels = algorithms.detect_communities(graph)

    grouped: dict[int, list[int]] = {}
    for node, community_id in labels.items():
        grouped.setdefault(community_id, []).append(node)

    users = _users_by_ids(session, list(labels.keys()))
    return [
        {
            "community": community_id,
            "members": [users.get(uid) for uid in members if uid in users],
        }
        for community_id, members in sorted(grouped.items())
    ]


@router.get("/components")
def components(session: SessionDep) -> list[list[UserPublic]]:
    """Connected components of the network (undirected reachability).

    Powered by ``algorithms.connected_components`` (Exercise 7).
    """
    graph = build_follow_graph(session)
    comps = algorithms.connected_components(graph)

    all_ids = [uid for comp in comps for uid in comp]
    users = _users_by_ids(session, all_ids)
    return [[users[uid] for uid in comp if uid in users] for comp in comps]
