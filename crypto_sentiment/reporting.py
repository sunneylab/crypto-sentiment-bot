"""Markdown report generation."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import sqlite3


def write_report(connection: sqlite3.Connection, output_dir: Path, recent: int = 100) -> Path:
    rows = connection.execute("SELECT * FROM articles ORDER BY fetched_at DESC LIMIT ?", (recent,)).fetchall()
    counts = Counter(row["sentiment"] for row in rows)
    sources = Counter(row["source"] for row in rows)
    average = sum(row["score"] for row in rows) / len(rows) if rows else 0
    lines = ["# Crypto Sentiment Report", "", f"Generated at (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}", "", f"Samples: {len(rows)}", f"Average sentiment score: {average:.2f}", f"Positive: {counts['positive']} / Neutral: {counts['neutral']} / Negative: {counts['negative']}", "", "## Sources", ""]
    lines.extend(f"- `{source}`: {count} articles" for source, count in sources.most_common())
    lines += ["", "## Articles", ""]
    lines.extend(f"- **{row['sentiment']} ({row['score']:+d})** [{row['title']}]({row['link']}) — {row['source']}" for row in rows)
    report = output_dir / "report.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report
