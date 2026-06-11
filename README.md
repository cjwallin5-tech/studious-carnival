# Social Network API

A starter social-networking API built with **FastAPI**, **SQLModel**, and **Alembic**.
It ships with authentication, users/profiles, posts, comments, likes, following, and a
personalized feed — a working foundation to build on and adjust.

## Quickstart

```bash
# 1. Create a virtual environment and install
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 2. Configure (defaults work out of the box)
cp .env.example .env

# 3. Create the database schema
alembic upgrade head

# 4. Run the API
uvicorn app.main:app --reload
```

Then open:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

> Click **Authorize** in Swagger UI and log in with a username/password
> (register one first via `POST /api/v1/auth/register`) to call protected endpoints.

## Project layout

```
app/
├── main.py              # FastAPI app, CORS, router wiring
├── core/
│   ├── config.py        # Settings loaded from .env
│   ├── database.py      # Engine + get_session dependency
│   └── security.py      # Password hashing + JWT helpers
├── models/              # SQLModel tables (User, Post, Comment, Like, Follow)
├── schemas/             # Request/response Pydantic models
└── api/
    ├── deps.py          # Shared dependencies (current user, db session)
    ├── router.py        # Aggregates all route modules
    └── routes/          # auth, users, posts, comments
alembic/                 # Migration environment + versions/
tests/                   # pytest suite (full API flow)
```

## API overview

All routes are prefixed with `/api/v1`.

### Auth (`/auth`)
| Method | Path             | Description                                   |
|--------|------------------|-----------------------------------------------|
| POST   | `/auth/register` | Create an account                             |
| POST   | `/auth/token`    | OAuth2 form login (used by Swagger Authorize) |
| POST   | `/auth/login`    | JSON login → access token                     |
| GET    | `/auth/me`       | Current authenticated user                    |

### Users (`/users`)
| Method | Path                       | Description                          |
|--------|----------------------------|--------------------------------------|
| GET    | `/users`                   | List/search users                    |
| PATCH  | `/users/me`                | Update your profile                  |
| GET    | `/users/{id}`              | Public profile + follow/post counts  |
| POST   | `/users/{id}/follow`       | Follow a user                        |
| DELETE | `/users/{id}/follow`       | Unfollow a user                      |
| GET    | `/users/{id}/followers`    | Users following this user            |
| GET    | `/users/{id}/following`    | Users this user follows              |

### Posts (`/posts`)
| Method | Path                    | Description                              |
|--------|-------------------------|------------------------------------------|
| POST   | `/posts`                | Create a post                            |
| GET    | `/posts`                | Public timeline (filter by `author_id`)  |
| GET    | `/posts/feed`           | Posts from people you follow + your own  |
| GET    | `/posts/{id}`           | Single post w/ like & comment counts     |
| PUT    | `/posts/{id}`           | Edit your post                           |
| DELETE | `/posts/{id}`           | Delete your post                         |
| POST   | `/posts/{id}/like`      | Like a post (idempotent)                 |
| DELETE | `/posts/{id}/like`      | Remove your like                         |

### Comments
| Method | Path                          | Description              |
|--------|-------------------------------|--------------------------|
| GET    | `/posts/{id}/comments`        | List a post's comments   |
| POST   | `/posts/{id}/comments`        | Add a comment            |
| PUT    | `/comments/{id}`              | Edit your comment        |
| DELETE | `/comments/{id}`              | Delete your comment      |

### Admin (`/admin`) — local development only
| Method | Path           | Description                                              |
|--------|----------------|----------------------------------------------------------|
| POST   | `/admin/reset` | Delete ALL data (users, posts, comments, likes, follows) |

The reset endpoint leaves the schema in place and is unauthenticated — it
exists for local development and the demo frontend. The same wipe is available
from the command line:

```bash
python scripts/reset_db.py        # asks for confirmation
python scripts/reset_db.py --yes  # skips the prompt
```

## Database & migrations

After changing anything in `app/models/`, generate and apply a migration:

```bash
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```

Other useful commands:

```bash
alembic downgrade -1     # roll back one revision
alembic history          # list migrations
alembic current          # show applied revision
```

### Switching to Postgres

Set `DATABASE_URL` in `.env`, e.g.:

```
DATABASE_URL="postgresql+psycopg://user:password@localhost:5432/social_network"
```

(The `psycopg` driver is already in the dependencies.) Then run `alembic upgrade head`.

## Tests

```bash
pytest
```

Tests run against an in-memory SQLite database and cover the full auth → post →
comment → like → follow → feed flow.

## Notes & next steps

This is intentionally a foundation. Some natural extensions:

- Refresh tokens / token revocation
- Pagination metadata (total counts, cursors)
- Image/media uploads
- Notifications, direct messages, hashtags, mentions
- Rate limiting and soft-deletes

Generated as a scaffold — adjust models, schemas, and routes freely.
