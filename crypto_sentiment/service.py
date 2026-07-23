"""Application service that coordinates sources, analysis, storage, and reports."""

from __future__ import annotations

import sys
from pathlib import Path

from .config import Settings
from .feeds import demo_articles, fetch_feed
from .models import Article
from .reporting import write_report
from .repository import open_database, save_articles


def deduplicate(articles: list[Article], limit: int) -> list[Article]:
    result: list[Article] = []
    seen: set[str] = set()
    for article in articles:
        if article.link not in seen:
            seen.add(article.link)
            result.append(article)
        if len(result) >= limit:
            break
    return result


def collect_once(settings: Settings, output_dir: Path, limit: int, demo: bool = False, report_limit: int = 100) -> tuple[int, int, Path]:
    articles = demo_articles(settings.positive_words, settings.negative_words) if demo else []
    if not demo:
        for url in settings.feeds:
            try:
                articles.extend(fetch_feed(url, settings.positive_words, settings.negative_words, settings.request_timeout))
            except Exception as exc:
                print(f"Skipping feed {url}: {exc}", file=sys.stderr)
    articles = deduplicate(articles, limit)
    connection = open_database(output_dir)
    try:
        inserted = save_articles(connection, articles)
        report = write_report(connection, output_dir, report_limit)
    finally:
        connection.close()
    return len(articles), inserted, report
