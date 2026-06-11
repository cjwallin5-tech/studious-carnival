from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.post import Post
    from app.models.user import User


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Comment(SQLModel, table=True):
    __tablename__ = "comments"

    id: int | None = Field(default=None, primary_key=True)
    content: str = Field(max_length=2000)
    post_id: int = Field(foreign_key="posts.id", index=True)
    author_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=_utcnow)

    # Relationships
    post: "Post" = Relationship(back_populates="comments")
    author: "User" = Relationship(back_populates="comments")
