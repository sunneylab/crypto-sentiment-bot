"""Aggregate sentiment signals for personal research dashboards."""

from __future__ import annotations

import sqlite3
from collections import Counter


def build_snapshot(connection: sqlite3.Connection, limit: int = 100) -> dict:
    rows = connection.execute("SELECT sentiment, score, source FROM articles ORDER BY fetched_at DESC LIMIT ?", (limit,)).fetchall()
    counts = Counter(row[0] for row in rows)
    total_score = sum(row[1] for row in rows)
    average = total_score / len(rows) if rows else 0
    mood = "bullish" if average >= 1 else "bearish" if average <= -1 else "mixed"
    return {"mood": mood, "sample_count": len(rows), "total_score": total_score, "average_score": round(average, 3), "positive": counts["positive"], "neutral": counts["neutral"], "negative": counts["negative"], "sources": dict(Counter(row[2] for row in rows))}
