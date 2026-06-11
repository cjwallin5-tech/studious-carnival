"""Wipe all data from the database (the schema is left intact).

Deletes every user, post, comment, like, and follow — the same thing the
frontend's "Reset database" button does via ``POST /api/v1/admin/reset``.

Usage (from the project root):

    python scripts/reset_db.py          # asks for confirmation
    python scripts/reset_db.py --yes    # skips the prompt
"""

import sys

from sqlmodel import Session

from app.api.routes.admin import wipe_all_data
from app.core.config import settings
from app.core.database import engine


def main() -> None:
    if "--yes" not in sys.argv:
        answer = input(f"Delete ALL data in {settings.DATABASE_URL}? [y/N] ")
        if answer.strip().lower() not in ("y", "yes"):
            print("Aborted.")
            return

    with Session(engine) as session:
        deleted = wipe_all_data(session)

    total = sum(deleted.values())
    print(f"Deleted {total} rows: " + ", ".join(f"{table}={n}" for table, n in deleted.items()))


if __name__ == "__main__":
    main()
