import sqlite3
import tempfile
import unittest
from pathlib import Path

from app import Article, DEFAULT_NEGATIVE, DEFAULT_POSITIVE, analyze, deduplicate, parse_feed, save_articles
from analytics import build_analytics
from crypto_sentiment.cleanup import delete_by_link
from crypto_sentiment.signals import build_snapshot


class SentimentTests(unittest.TestCase):
    def test_positive_and_negative_terms(self):
        label, score, hits = analyze("Bullish adoption but also hack risk", DEFAULT_POSITIVE, DEFAULT_NEGATIVE)
        self.assertEqual(label, "neutral")
        self.assertEqual(score, 0)
        self.assertIn("adoption", hits)
        self.assertIn("hack", hits)

    def test_deduplicate_and_limit(self):
        items = [Article("A", "https://example.com/a", "", "test"), Article("A copy", "https://example.com/a", "", "test"), Article("B", "https://example.com/b", "", "test")]
        self.assertEqual([item.title for item in deduplicate(items, 10)], ["A", "B"])

    def test_rss_parser(self):
        payload = b"<rss><channel><item><title>Bitcoin rally</title><link>https://example.com/1</link><description>strong gain</description></item></channel></rss>"
        items = parse_feed(payload, "fixture", DEFAULT_POSITIVE, DEFAULT_NEGATIVE)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].sentiment, "positive")

    def test_database_ignores_duplicate_links(self):
        with tempfile.TemporaryDirectory() as directory:
            connection = sqlite3.connect(Path(directory) / "test.db")
            connection.execute("CREATE TABLE articles (id TEXT PRIMARY KEY, title TEXT, link TEXT UNIQUE, summary TEXT, source TEXT, published TEXT, sentiment TEXT, score INTEGER, fetched_at TEXT, created_at TEXT)")
            article = Article("A", "https://example.com/a", "", "test", fetched_at="2026-01-01T00:00:00+00:00")
            self.assertEqual(save_articles(connection, [article, article]), 1)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM articles").fetchone()[0], 1)
            connection.close()

    def test_analytics_groups_daily_counts(self):
        rows = [
            {"fetched_at": "2026-01-01T00:00:00+00:00", "sentiment": "positive", "score": 2, "source": "a", "title": "Bitcoin rally"},
            {"fetched_at": "2026-01-01T01:00:00+00:00", "sentiment": "negative", "score": -1, "source": "b", "title": "Bitcoin crash"},
        ]
        result = build_analytics(rows)
        self.assertEqual(result["daily"]["2026-01-01"]["score"], 1)
        self.assertEqual(result["sources"], {"a": 1, "b": 1})

    def test_snapshot_classifies_recent_mood(self):
        connection = sqlite3.connect(":memory:")
        connection.execute("CREATE TABLE articles (sentiment TEXT, score INTEGER, source TEXT, fetched_at TEXT)")
        connection.executemany("INSERT INTO articles VALUES (?, ?, ?, ?)", [("positive", 2, "a", "2026-01-01") for _ in range(3)])
        snapshot = build_snapshot(connection)
        self.assertEqual(snapshot["mood"], "bullish")
        self.assertEqual(snapshot["sample_count"], 3)
        connection.close()

    def test_cleanup_deletes_exact_link(self):
        connection = sqlite3.connect(":memory:")
        connection.execute("CREATE TABLE articles (link TEXT UNIQUE, fetched_at TEXT)")
        connection.execute("INSERT INTO articles VALUES (?, ?)", ("https://example.com/delete", "2020-01-01"))
        self.assertEqual(delete_by_link(connection, "https://example.com/delete"), 1)
        self.assertEqual(connection.execute("SELECT COUNT(*) FROM articles").fetchone()[0], 0)
        connection.close()


if __name__ == "__main__":
    unittest.main()
