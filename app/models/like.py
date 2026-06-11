from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

if TYPE_CHECKING:
    from app.models.post import Post
    from app.models.user import User


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Like(SQLModel, table=True):
    __tablename__ = "likes"
    # A user can like a given post at most once.
    __table_args__ = (UniqueConstraint("user_id", "post_id", name="uq_like_user_post"),)

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    post_id: int = Field(foreign_key="posts.id", index=True)
    created_at: datetime = Field(default_factory=_utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="likes")
    post: "Post" = Relationship(back_populates="likes")
