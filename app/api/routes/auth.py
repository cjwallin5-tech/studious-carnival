from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import or_, select

from app.api.deps import CurrentUser, SessionDep
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


def _authenticate(session: SessionDep, username: str, password: str) -> User:
    # Allow login with either username or email.
    user = session.exec(
        select(User).where(or_(User.username == username, User.email == username))
    ).first()
    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, session: SessionDep) -> User:
    existing = session.exec(
        select(User).where(or_(User.username == payload.username, User.email == payload.email))
    ).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with that username or email already exists",
        )

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        bio=payload.bio,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/token", response_model=Token)
def login_form(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """OAuth2 password-flow endpoint — used by the Swagger "Authorize" button."""
    user = _authenticate(session, form_data.username, form_data.password)
    return Token(access_token=create_access_token(user.id))


@router.post("/login", response_model=Token)
def login_json(payload: LoginRequest, session: SessionDep) -> Token:
    """JSON-friendly login for SPA / mobile clients."""
    user = _authenticate(session, payload.username, payload.password)
    return Token(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserRead)
def read_me(current_user: CurrentUser) -> User:
    return current_user
