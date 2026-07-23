#!/usr/bin/env python3
"""Write an aggregate sentiment snapshot from the local database."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from crypto_sentiment.repository import open_database
from crypto_sentiment.signals import build_snapshot


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local sentiment snapshot")
    parser.add_argument("--output-dir", type=Path, default=Path("data"))
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--output", type=Path, default=Path("data/snapshot.json"))
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("limit must be greater than zero")
    connection = open_database(args.output_dir)
    try:
        snapshot = build_snapshot(connection, args.limit)
    finally:
        connection.close()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    print(f"Snapshot mood: {snapshot['mood']}; records: {snapshot['sample_count']}")
    print(f"Snapshot written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
