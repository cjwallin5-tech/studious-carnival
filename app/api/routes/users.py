from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Follow, Post, User
from app.schemas.user import UserProfile, UserPublic, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


def _build_profile(session: SessionDep, user: User) -> UserProfile:
    followers_count = session.exec(
        select(func.count()).select_from(Follow).where(Follow.following_id == user.id)
    ).one()
    following_count = session.exec(
        select(func.count()).select_from(Follow).where(Follow.follower_id == user.id)
    ).one()
    posts_count = session.exec(
        select(func.count()).select_from(Post).where(Post.author_id == user.id)
    ).one()
    return UserProfile(
        **UserPublic.model_validate(user).model_dump(),
        followers_count=followers_count,
        following_count=following_count,
        posts_count=posts_count,
    )


def _get_user_or_404(session: SessionDep, user_id: int) -> User:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("", response_model=list[UserPublic])
def list_users(
    session: SessionDep,
    q: str | None = Query(default=None, description="Filter by username substring"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[User]:
    statement = select(User)
    if q:
        statement = statement.where(User.username.contains(q))
    statement = statement.offset(offset).limit(limit)
    return list(session.exec(statement).all())


@router.patch("/me", response_model=UserRead)
def update_me(payload: UserUpdate, session: SessionDep, current_user: CurrentUser) -> User:
    data = payload.model_dump(exclude_unset=True)

    if "email" in data and data["email"] != current_user.email:
        clash = session.exec(select(User).where(User.email == data["email"])).first()
        if clash is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")

    for key, value in data.items():
        setattr(current_user, key, value)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.get("/{user_id}", response_model=UserProfile)
def get_user(user_id: int, session: SessionDep) -> UserProfile:
    user = _get_user_or_404(session, user_id)
    return _build_profile(session, user)


@router.post("/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
def follow_user(user_id: int, session: SessionDep, current_user: CurrentUser) -> None:
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot follow yourself"
        )
    _get_user_or_404(session, user_id)

    existing = session.exec(
        select(Follow).where(Follow.follower_id == current_user.id, Follow.following_id == user_id)
    ).first()
    if existing is None:
        session.add(Follow(follower_id=current_user.id, following_id=user_id))
        session.commit()


@router.delete("/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
def unfollow_user(user_id: int, session: SessionDep, current_user: CurrentUser) -> None:
    existing = session.exec(
        select(Follow).where(Follow.follower_id == current_user.id, Follow.following_id == user_id)
    ).first()
    if existing is not None:
        session.delete(existing)
        session.commit()


@router.get("/{user_id}/followers", response_model=list[UserPublic])
def list_followers(user_id: int, session: SessionDep) -> list[User]:
    _get_user_or_404(session, user_id)
    statement = (
        select(User)
        .join(Follow, Follow.follower_id == User.id)
        .where(Follow.following_id == user_id)
    )
    return list(session.exec(statement).all())


@router.get("/{user_id}/following", response_model=list[UserPublic])
def list_following(user_id: int, session: SessionDep) -> list[User]:
    _get_user_or_404(session, user_id)
    statement = (
        select(User)
        .join(Follow, Follow.following_id == User.id)
        .where(Follow.follower_id == user_id)
    )
    return list(session.exec(statement).all())
