"""SQLite persistence adapter."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from .models import Article


def open_database(output_dir: Path) -> sqlite3.Connection:
    output_dir.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(output_dir / "sentiment.db")
    connection.row_factory = sqlite3.Row
    connection.execute("""CREATE TABLE IF NOT EXISTS articles (
        id TEXT PRIMARY KEY, title TEXT NOT NULL, link TEXT UNIQUE NOT NULL,
        summary TEXT, source TEXT, published TEXT, sentiment TEXT, score INTEGER,
        fetched_at TEXT NOT NULL, created_at TEXT NOT NULL
    )""")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_articles_fetched ON articles(fetched_at)")
    connection.commit()
    return connection


def save_articles(connection: sqlite3.Connection, articles: list[Article]) -> int:
    inserted = 0
    for article in articles:
        cursor = connection.execute("""INSERT OR IGNORE INTO articles
            (id,title,link,summary,source,published,sentiment,score,fetched_at,created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?)""", (
                article.article_id, article.title, article.link, article.summary,
                article.source, article.published, article.sentiment, article.score,
                article.fetched_at, article.fetched_at,
            ))
        inserted += cursor.rowcount
    connection.commit()
    return inserted
