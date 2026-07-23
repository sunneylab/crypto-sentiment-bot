"""Public RSS/Atom ingestion adapters."""

from __future__ import annotations

import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from .analyzer import analyze
from .models import Article
from .text import clean_text


def _first_text(element: ET.Element, names: tuple[str, ...]) -> str:
    for child in list(element):
        if child.tag.rsplit("}", 1)[-1].lower() in names and child.text:
            return clean_text(child.text)
    return ""


def parse_feed(payload: bytes, source: str, positive: set[str] | frozenset[str], negative: set[str] | frozenset[str]) -> list[Article]:
    root = ET.fromstring(payload)
    entries = [node for node in root.iter() if node.tag.rsplit("}", 1)[-1].lower() in {"item", "entry"}]
    fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    result: list[Article] = []
    for entry in entries:
        link = _first_text(entry, ("link", "guid"))
        if not link:
            for child in list(entry):
                if child.tag.rsplit("}", 1)[-1].lower() == "link":
                    link = child.attrib.get("href", "")
                    break
        title = _first_text(entry, ("title",))
        summary = _first_text(entry, ("description", "summary", "content"))
        published = _first_text(entry, ("pubdate", "published", "updated"))
        label, score, _ = analyze(f"{title} {summary}", positive, negative)
        if title and link:
            result.append(Article(title, link, summary, source, published, label, score, fetched_at))
    return result


def fetch_feed(url: str, positive: set[str] | frozenset[str], negative: set[str] | frozenset[str], timeout: int = 15) -> list[Article]:
    request = urllib.request.Request(url, headers={"User-Agent": "crypto-sentiment-bot/0.3 (read-only)"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return parse_feed(response.read(), url, positive, negative)


def demo_articles(positive: set[str] | frozenset[str], negative: set[str] | frozenset[str]) -> list[Article]:
    examples = [
        ("Bitcoin adoption grows as institutions report strong demand", "https://example.com/demo/1"),
        ("Market risk rises after exchange hack concerns", "https://example.com/demo/2"),
        ("Crypto market remains mixed ahead of new data", "https://example.com/demo/3"),
    ]
    fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return [Article(title, link, "Offline demo item", "demo", "", *analyze(title, positive, negative)[:2], fetched_at) for title, link in examples]
