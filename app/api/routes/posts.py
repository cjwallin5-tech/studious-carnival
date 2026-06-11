from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Comment, Follow, Like, Post, User
from app.schemas.post import PostCreate, PostRead, PostUpdate

router = APIRouter(prefix="/posts", tags=["posts"])


def _serialize(session: SessionDep, post: Post, current_user_id: int | None) -> PostRead:
    likes_count = session.exec(
        select(func.count()).select_from(Like).where(Like.post_id == post.id)
    ).one()
    comments_count = session.exec(
        select(func.count()).select_from(Comment).where(Comment.post_id == post.id)
    ).one()
    liked_by_me = False
    if current_user_id is not None:
        liked_by_me = (
            session.exec(
                select(Like).where(Like.post_id == post.id, Like.user_id == current_user_id)
            ).first()
            is not None
        )

    data = PostRead.model_validate(post).model_dump()
    data.update(
        likes_count=likes_count,
        comments_count=comments_count,
        liked_by_me=liked_by_me,
    )
    return PostRead(**data)


def _get_post_or_404(session: SessionDep, post_id: int) -> Post:
    post = session.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(payload: PostCreate, session: SessionDep, current_user: CurrentUser) -> PostRead:
    post = Post(content=payload.content, author_id=current_user.id)
    session.add(post)
    session.commit()
    session.refresh(post)
    return _serialize(session, post, current_user.id)


@router.get("", response_model=list[PostRead])
def list_posts(
    session: SessionDep,
    author_id: int | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[PostRead]:
    """Public timeline of all posts, newest first. Optionally filter by author."""
    statement = select(Post).order_by(Post.created_at.desc())
    if author_id is not None:
        statement = statement.where(Post.author_id == author_id)
    statement = statement.offset(offset).limit(limit)
    posts = session.exec(statement).all()
    return [_serialize(session, post, None) for post in posts]


@router.get("/feed", response_model=list[PostRead])
def my_feed(
    session: SessionDep,
    current_user: CurrentUser,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[PostRead]:
    """Posts from the users the current user follows, plus their own, newest first."""
    followed_ids = session.exec(
        select(Follow.following_id).where(Follow.follower_id == current_user.id)
    ).all()
    author_ids = [*followed_ids, current_user.id]

    statement = (
        select(Post)
        .where(Post.author_id.in_(author_ids))
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    posts = session.exec(statement).all()
    return [_serialize(session, post, current_user.id) for post in posts]


@router.get("/{post_id}", response_model=PostRead)
def get_post(post_id: int, session: SessionDep) -> PostRead:
    post = _get_post_or_404(session, post_id)
    return _serialize(session, post, None)


@router.put("/{post_id}", response_model=PostRead)
def update_post(
    post_id: int, payload: PostUpdate, session: SessionDep, current_user: CurrentUser
) -> PostRead:
    post = _get_post_or_404(session, post_id)
    if post.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your post")
    from datetime import datetime, timezone

    post.content = payload.content
    post.updated_at = datetime.now(timezone.utc)
    session.add(post)
    session.commit()
    session.refresh(post)
    return _serialize(session, post, current_user.id)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, session: SessionDep, current_user: CurrentUser) -> None:
    post = _get_post_or_404(session, post_id)
    if post.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your post")
    session.delete(post)
    session.commit()


@router.post("/{post_id}/like", status_code=status.HTTP_204_NO_CONTENT)
def like_post(post_id: int, session: SessionDep, current_user: CurrentUser) -> None:
    _get_post_or_404(session, post_id)
    existing = session.exec(
        select(Like).where(Like.post_id == post_id, Like.user_id == current_user.id)
    ).first()
    if existing is None:
        session.add(Like(post_id=post_id, user_id=current_user.id))
        session.commit()


@router.delete("/{post_id}/like", status_code=status.HTTP_204_NO_CONTENT)
def unlike_post(post_id: int, session: SessionDep, current_user: CurrentUser) -> None:
    existing = session.exec(
        select(Like).where(Like.post_id == post_id, Like.user_id == current_user.id)
    ).first()
    if existing is not None:
        session.delete(existing)
        session.commit()
