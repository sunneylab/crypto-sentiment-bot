"""Domain objects with no I/O dependencies."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class Article:
    title: str
    link: str
    summary: str
    source: str
    published: str = ""
    sentiment: str = "neutral"
    score: int = 0
    fetched_at: str = ""

    @property
    def article_id(self) -> str:
        return hashlib.sha256(self.link.encode("utf-8")).hexdigest()
