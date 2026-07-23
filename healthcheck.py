#!/usr/bin/env python3
"""Read-only feed and local configuration health check."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse


def check_feed(url: str, timeout: int = 10) -> dict:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return {"url": url, "ok": False, "error": "URL must use http or https"}
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "crypto-sentiment-bot-health/0.1"})
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return {"url": url, "ok": 200 <= response.status < 400, "status": response.status, "latency_ms": round((time.perf_counter() - started) * 1000)}
    except urllib.error.HTTPError as exc:
        return {"url": url, "ok": False, "status": exc.code, "error": str(exc.reason)}
    except Exception as exc:
        return {"url": url, "ok": False, "error": str(exc)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Check configured public feeds")
    parser.add_argument("--config", type=Path, default=Path("config.json"))
    parser.add_argument("--output", type=Path, default=Path("data/health.json"))
    args = parser.parse_args()
    if not args.config.exists():
        parser.error(f"Config file not found: {args.config}")
    config = json.loads(args.config.read_text(encoding="utf-8"))
    results = [check_feed(url) for url in config.get("feeds", [])]
    payload = {"ok": bool(results) and all(item["ok"] for item in results), "feeds": results}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    for item in results:
        print(f"{'OK' if item['ok'] else 'FAIL'} {item['url']}")
    print(f"Health report: {args.output}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
