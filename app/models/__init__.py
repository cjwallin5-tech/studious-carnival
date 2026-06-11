"""SQLModel table models.

Importing them here ensures Alembic's autogenerate and SQLModel.metadata
see every table.
"""

from app.models.comment import Comment
from app.models.follow import Follow
from app.models.like import Like
from app.models.post import Post
from app.models.user import User

__all__ = ["User", "Post", "Comment", "Like", "Follow"]
