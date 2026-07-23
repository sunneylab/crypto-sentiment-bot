#!/usr/bin/env python3
"""Delete selected local records or apply a local retention window."""

from __future__ import annotations

import argparse
from pathlib import Path

from crypto_sentiment.cleanup import delete_by_link, delete_older_than
from crypto_sentiment.repository import open_database


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage local sentiment retention")
    parser.add_argument("--output-dir", type=Path, default=Path("data"))
    parser.add_argument("--link", help="delete one exact article link")
    parser.add_argument("--older-than", type=int, help="delete records older than this many days")
    args = parser.parse_args()
    if bool(args.link) == (args.older_than is None):
        parser.error("choose exactly one of --link or --older-than")
    connection = open_database(args.output_dir)
    try:
        deleted = delete_by_link(connection, args.link) if args.link else delete_older_than(connection, args.older_than)
    finally:
        connection.close()
    print(f"Deleted {deleted} local records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
