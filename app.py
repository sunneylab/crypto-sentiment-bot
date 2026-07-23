#!/usr/bin/env python3
"""CLI composition root for the layered crypto sentiment application."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

# Public compatibility exports for existing scripts and tests.
from crypto_sentiment.analyzer import analyze
from crypto_sentiment.config import DEFAULT_NEGATIVE, DEFAULT_POSITIVE, load_settings
from crypto_sentiment.feeds import demo_articles, fetch_feed, parse_feed
from crypto_sentiment.models import Article
from crypto_sentiment.repository import open_database, save_articles
from crypto_sentiment.service import collect_once, deduplicate


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only crypto RSS sentiment collector")
    parser.add_argument("--config", type=Path, default=Path("config.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("data"))
    parser.add_argument("--limit", type=int, default=30, help="maximum items processed per cycle")
    parser.add_argument("--report-limit", type=int, default=100, help="number of historical items shown in the report")
    parser.add_argument("--interval", type=int, help="polling interval in seconds")
    parser.add_argument("--demo", action="store_true", help="run offline without network access")
    parser.add_argument("--watch", action="store_true", help="poll continuously until Ctrl+C")
    args = parser.parse_args()
    if args.limit < 1 or args.report_limit < 1:
        parser.error("--limit and --report-limit must be greater than zero")
    if not args.demo and not args.config.exists():
        parser.error(f"Config file not found: {args.config}. Copy config.example.json to config.json.")
    try:
        settings = load_settings(args.config, require_feeds=not args.demo) if not args.demo else load_settings(args.config, require_feeds=False) if args.config.exists() else load_settings(Path("config.example.json"), require_feeds=False)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    interval = args.interval or settings.interval_seconds
    if interval < 1:
        parser.error("polling interval must be greater than zero")
    try:
        while True:
            fetched, inserted, report = collect_once(settings, args.output_dir, args.limit, args.demo, args.report_limit)
            print(f"Fetched {fetched} items; inserted {inserted} new items. Report: {report}")
            if not args.watch:
                break
            print(f"Waiting {interval} seconds before the next cycle. Press Ctrl+C to exit.")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nPolling stopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
