"""Configuration loading and validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

DEFAULT_POSITIVE = {"bullish", "surge", "rally", "adoption", "approval", "gain", "positive", "strong"}
DEFAULT_NEGATIVE = {"bearish", "crash", "dump", "hack", "lawsuit", "ban", "loss", "negative", "weak", "risk"}


@dataclass(frozen=True)
class Settings:
    feeds: tuple[str, ...]
    positive_words: frozenset[str]
    negative_words: frozenset[str]
    interval_seconds: int = 900
    request_timeout: int = 15


def load_settings(path: Path, require_feeds: bool = True) -> Settings:
    data = json.loads(path.read_text(encoding="utf-8"))
    feeds = tuple(str(url).strip() for url in data.get("feeds", []) if str(url).strip())
    if require_feeds and not feeds:
        raise ValueError("The config file has no feeds.")
    interval = int(data.get("interval_seconds", 900))
    timeout = int(data.get("request_timeout", 15))
    if interval < 1 or timeout < 1:
        raise ValueError("interval_seconds and request_timeout must be greater than zero.")
    return Settings(
        feeds=feeds,
        positive_words=frozenset(data.get("positive_words", DEFAULT_POSITIVE)),
        negative_words=frozenset(data.get("negative_words", DEFAULT_NEGATIVE)),
        interval_seconds=interval,
        request_timeout=timeout,
    )
