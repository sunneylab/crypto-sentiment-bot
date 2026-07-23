"""Pure sentiment scoring logic."""

from __future__ import annotations

from .text import clean_text


def analyze(text: str, positive: set[str] | frozenset[str], negative: set[str] | frozenset[str]) -> tuple[str, int, list[str]]:
    normalized = clean_text(text).lower()
    positive_hits = [word for word in positive if word.lower() in normalized]
    negative_hits = [word for word in negative if word.lower() in normalized]
    score = len(positive_hits) - len(negative_hits)
    label = "positive" if score > 0 else "negative" if score < 0 else "neutral"
    return label, score, positive_hits + negative_hits
