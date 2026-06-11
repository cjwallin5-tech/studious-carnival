"""Admin / development endpoints.

These are conveniences for local development and the classroom demo frontend.
They are NOT protected by authentication — like the graph routes, this app is
meant to run locally. Don't expose this API to the internet as-is.
"""

from sqlmodel import Session, delete
from fastapi import APIRouter

from app.api.deps import SessionDep
from app.models import Comment, Follow, Like, Post, User

router = APIRouter(prefix="/admin", tags=["admin"])

# Children before parents so foreign keys are never violated mid-wipe.
_WIPE_ORDER = (Comment, Like, Follow, Post, User)


def wipe_all_data(session: Session) -> dict[str, int]:
    """Delete every row from every table (the schema is left intact).

    Returns a mapping of table name -> number of rows deleted. Also used by
    ``scripts/reset_db.py``.
    """
    deleted: dict[str, int] = {}
    for model in _WIPE_ORDER:
        result = session.exec(delete(model))
        deleted[model.__tablename__] = result.rowcount
    session.commit()
    return deleted


@router.post("/reset")
def reset_database(session: SessionDep) -> dict:
    """Delete all users, posts, comments, likes, and follows.

    The schema stays in place, so the API is immediately usable again
    (e.g. re-seed from the frontend). Irreversible — use with care.
    """
    return {"deleted": wipe_all_data(session)}
