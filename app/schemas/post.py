from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.user import UserPublic


class PostCreate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class PostUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class PostRead(BaseModel):
    id: int
    content: str
    author_id: int
    created_at: datetime
    updated_at: datetime
    author: UserPublic
    likes_count: int = 0
    comments_count: int = 0
    liked_by_me: bool = False

    model_config = {"from_attributes": True}
