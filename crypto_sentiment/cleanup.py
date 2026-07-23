"""Local data retention and deletion operations."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone


def delete_by_link(connection: sqlite3.Connection, link: str) -> int:
    cursor = connection.execute("DELETE FROM articles WHERE link = ?", (link,))
    connection.commit()
    return cursor.rowcount


def delete_older_than(connection: sqlite3.Connection, days: int) -> int:
    if days < 1:
        raise ValueError("days must be greater than zero")
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(timespec="seconds")
    cursor = connection.execute("DELETE FROM articles WHERE fetched_at < ?", (cutoff,))
    connection.commit()
    return cursor.rowcount
