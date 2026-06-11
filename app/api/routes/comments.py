from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import Comment, Post
from app.schemas.comment import CommentCreate, CommentRead, CommentUpdate

router = APIRouter(tags=["comments"])


def _get_comment_or_404(session: SessionDep, comment_id: int) -> Comment:
    comment = session.get(Comment, comment_id)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment


@router.get("/posts/{post_id}/comments", response_model=list[CommentRead])
def list_comments(
    post_id: int,
    session: SessionDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[Comment]:
    if session.get(Post, post_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    statement = (
        select(Comment)
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc())
        .offset(offset)
        .limit(limit)
    )
    return list(session.exec(statement).all())


@router.post(
    "/posts/{post_id}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    post_id: int, payload: CommentCreate, session: SessionDep, current_user: CurrentUser
) -> Comment:
    if session.get(Post, post_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    comment = Comment(content=payload.content, post_id=post_id, author_id=current_user.id)
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment


@router.put("/comments/{comment_id}", response_model=CommentRead)
def update_comment(
    comment_id: int,
    payload: CommentUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Comment:
    comment = _get_comment_or_404(session, comment_id)
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your comment")
    comment.content = payload.content
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, session: SessionDep, current_user: CurrentUser) -> None:
    comment = _get_comment_or_404(session, comment_id)
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your comment")
    session.delete(comment)
    session.commit()
