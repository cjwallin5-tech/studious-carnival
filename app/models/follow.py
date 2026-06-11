from datetime import datetime, timezone

from sqlmodel import Field, SQLModel, UniqueConstraint


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Follow(SQLModel, table=True):
    """A directed follow edge: `follower_id` follows `following_id`."""

    __tablename__ = "follows"
    __table_args__ = (UniqueConstraint("follower_id", "following_id", name="uq_follow_pair"),)

    id: int | None = Field(default=None, primary_key=True)
    follower_id: int = Field(foreign_key="users.id", index=True)
    following_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=_utcnow)
