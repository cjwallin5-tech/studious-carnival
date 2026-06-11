from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.user import UserPublic


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class CommentUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class CommentRead(BaseModel):
    id: int
    content: str
    post_id: int
    author_id: int
    created_at: datetime
    author: UserPublic

    model_config = {"from_attributes": True}
