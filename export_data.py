#!/usr/bin/env python3
"""Export local sentiment history without contacting any remote service."""

from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from pathlib import Path


def read_rows(database: Path, limit: int) -> list[dict]:
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in connection.execute(
            "SELECT id,title,link,summary,source,published,sentiment,score,fetched_at,created_at "
            "FROM articles ORDER BY fetched_at DESC LIMIT ?", (limit,)
        )]
    finally:
        connection.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Export local sentiment history")
    parser.add_argument("--database", type=Path, default=Path("data/sentiment.db"))
    parser.add_argument("--format", choices=("json", "csv"), default="json")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--limit", type=int, default=1000)
    args = parser.parse_args()
    if not args.database.exists():
        parser.error(f"Database not found: {args.database}")
    if args.limit < 1:
        parser.error("limit must be greater than zero")
    rows = read_rows(args.database, args.limit)
    output = args.output or Path(f"articles.{args.format}")
    if args.format == "json":
        output.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        with output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=rows[0].keys() if rows else ["id", "title", "link"])
            writer.writeheader()
            writer.writerows(rows)
    print(f"Exported {len(rows)} records to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
