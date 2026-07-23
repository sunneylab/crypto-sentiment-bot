#!/usr/bin/env python3
"""Small local read-only dashboard for the SQLite sentiment database."""

from __future__ import annotations

import argparse
import json
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from analytics import build_analytics, load_rows
from crypto_sentiment.signals import build_snapshot


def query_database(database: Path, limit: int = 100) -> dict:
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(
            "SELECT title, link, source, published, sentiment, score, fetched_at "
            "FROM articles ORDER BY fetched_at DESC LIMIT ?", (limit,)
        ).fetchall()
        counts = connection.execute(
            "SELECT sentiment, COUNT(*) AS count FROM articles GROUP BY sentiment"
        ).fetchall()
        analytics = build_analytics(load_rows(database, 3650))
        return {"articles": [dict(row) for row in rows], "counts": {row[0]: row[1] for row in counts}, "analytics": analytics, "snapshot": build_snapshot(connection)}
    finally:
        connection.close()


def render_page(payload: dict) -> str:
    counts = payload["counts"]
    snapshot = payload["snapshot"]
    cards = "".join(
        f'<tr><td><span class="{item["sentiment"]}">{item["sentiment"]}</span></td>'
        f'<td>{item["score"]:+d}</td><td><a href="{item["link"]}" target="_blank">{item["title"]}</a></td>'
        f'<td>{item["source"]}</td></tr>' for item in payload["articles"]
    )
    trend = payload["analytics"]["daily"]
    terms = ", ".join(f"{key} ({value})" for key, value in payload["analytics"]["top_terms"].items()) or "No terms yet"
    trend_rows = "".join(f"<tr><td>{day}</td><td>{item['positive']}</td><td>{item['neutral']}</td><td>{item['negative']}</td><td>{item['score']:+d}</td></tr>" for day, item in sorted(trend.items(), reverse=True))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Crypto Sentiment Dashboard</title><style>
body{{font:16px system-ui,sans-serif;max-width:1100px;margin:32px auto;padding:0 16px;background:#f5f7fb;color:#19202a}}
.cards{{display:flex;gap:12px;flex-wrap:wrap}}.card{{background:white;border-radius:10px;padding:16px 24px;box-shadow:0 2px 8px #0001}}
table{{width:100%;margin-top:24px;background:white;border-collapse:collapse}}th,td{{padding:12px;border-bottom:1px solid #e5e7eb;text-align:left}}
.positive{{color:#087f5b}}.negative{{color:#c92a2a}}.neutral{{color:#59636e}}a{{color:#185adb}}
</style></head><body><h1>Crypto Sentiment Dashboard</h1>
<div class="cards"><div class="card">Mood<br><strong>{snapshot["mood"]}</strong></div><div class="card">Positive<br><strong>{counts.get("positive", 0)}</strong></div>
<div class="card">Neutral<br><strong>{counts.get("neutral", 0)}</strong></div>
<div class="card">Negative<br><strong>{counts.get("negative", 0)}</strong></div></div>
<p><strong>Top terms:</strong> {terms}</p>
<h2>Daily trend</h2><table><thead><tr><th>Date</th><th>Positive</th><th>Neutral</th><th>Negative</th><th>Score</th></tr></thead><tbody>{trend_rows}</tbody></table>
<h2>Articles</h2><table><thead><tr><th>Sentiment</th><th>Score</th><th>Article</th><th>Source</th></tr></thead><tbody>{cards}</tbody></table>
</body></html>"""


def make_handler(database: Path):
    class DashboardHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            route = urlparse(self.path).path
            if route == "/api/articles":
                body = json.dumps(query_database(database), ensure_ascii=False).encode("utf-8")
                content_type = "application/json; charset=utf-8"
            elif route in {"/", "/index.html"}:
                body = render_page(query_database(database))[0:].encode("utf-8")
                content_type = "text/html; charset=utf-8"
            else:
                self.send_error(404, "Not found")
                return
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:
            return

    return DashboardHandler


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve a local read-only sentiment dashboard")
    parser.add_argument("--database", type=Path, default=Path("data/sentiment.db"))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if not args.database.exists():
        parser.error(f"Database not found: {args.database}. Run app.py first.")
    server = ThreadingHTTPServer((args.host, args.port), make_handler(args.database))
    print(f"Dashboard listening at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
