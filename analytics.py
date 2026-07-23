#!/usr/bin/env python3
"""Historical analytics for the local sentiment database."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

DEFAULT_STOP_WORDS = {"the", "and", "for", "with", "from", "that", "this", "crypto", "market", "about"}


def load_rows(database: Path, days: int) -> list[sqlite3.Row]:
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    try:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(timespec="seconds")
        return connection.execute("SELECT * FROM articles WHERE fetched_at >= ? ORDER BY fetched_at", (cutoff,)).fetchall()
    finally:
        connection.close()


def build_analytics(rows: list[sqlite3.Row], stop_words: set[str] | None = None) -> dict:
    stop_words = stop_words or DEFAULT_STOP_WORDS
    daily: dict[str, dict[str, int]] = {}
    sources: Counter[str] = Counter()
    terms: Counter[str] = Counter()
    for row in rows:
        day = row["fetched_at"][:10]
        daily.setdefault(day, {"positive": 0, "neutral": 0, "negative": 0, "score": 0})
        daily[day][row["sentiment"]] += 1
        daily[day]["score"] += row["score"]
        sources[row["source"]] += 1
        words = re.findall(r"[a-zA-Z][a-zA-Z0-9'-]{2,}", row["title"].lower())
        terms.update(word for word in words if word not in stop_words)
    return {
        "sample_count": len(rows),
        "average_score": round(sum(row["score"] for row in rows) / len(rows), 3) if rows else 0,
        "daily": daily,
        "sources": dict(sources.most_common()),
        "top_terms": dict(terms.most_common(20)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build local sentiment trend analytics")
    parser.add_argument("--database", type=Path, default=Path("data/sentiment.db"))
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--output", type=Path, default=Path("data/analytics.json"))
    args = parser.parse_args()
    if not args.database.exists():
        parser.error(f"Database not found: {args.database}")
    if args.days < 1:
        parser.error("days must be greater than zero")
    result = build_analytics(load_rows(args.database, args.days))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote analytics for {result['sample_count']} records to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
