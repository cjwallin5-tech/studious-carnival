from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)
    bio: str | None = Field(default=None, max_length=500)


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=255)
    bio: str | None = Field(default=None, max_length=500)
    email: EmailStr | None = None


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str | None
    bio: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserPublic(BaseModel):
    """A trimmed view safe to expose for other users (no email)."""

    id: int
    username: str
    full_name: str | None
    bio: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserProfile(UserPublic):
    """Public profile augmented with follow counts."""

    followers_count: int = 0
    following_count: int = 0
    posts_count: int = 0
