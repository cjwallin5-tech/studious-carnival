from collections.abc import Generator

from sqlmodel import Session, create_engine

from app.core.config import settings

# SQLite needs check_same_thread=False to be used across FastAPI's threadpool.
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args=connect_args,
)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session per request."""
    with Session(engine) as session:
        yield session
