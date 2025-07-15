"""Abusive word detection utilities for scanning messages."""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Iterable, Set
import string

logger = logging.getLogger(__name__)

BANNED_WORDS: Set[str] = set()
_WORDS_FILE: Path | None = None

_PUNCT_TABLE = str.maketrans({p: " " for p in string.punctuation})


def _normalize(text: str) -> str:
    """Lowercase ``text`` and replace common punctuation with spaces."""
    return text.lower().translate(_PUNCT_TABLE)


def _resolve_path(path: str) -> Path:
    """Return an absolute path for ``path`` relative to the project root."""
    p = Path(path)
    if not p.is_absolute():
        root = Path(__file__).resolve().parents[1]
        p = Path(os.path.join(root, path))
    return p


def load_words(path: str = "banned_words.txt") -> Set[str]:
    """Load words from ``path`` into a set of clean lowercase strings."""
    p = _resolve_path(path)
    if not p.exists():
        raise FileNotFoundError(f"[ABUSE] banned_words.txt not found at {p}")
    with p.open("r", encoding="utf-8") as f:
        words = {line.strip().lower() for line in f if line.strip()}
    logger.debug("[ABUSE] Loaded %d banned words from %s", len(words), p)
    return words


def init_words(path: str = "banned_words.txt") -> None:
    """Initialize the global :data:`BANNED_WORDS` set from ``path``."""
    global BANNED_WORDS, _WORDS_FILE
    _WORDS_FILE = _resolve_path(path)
    BANNED_WORDS = load_words(_WORDS_FILE)
    logger.info("[ABUSE] Initialized banned words (%d): %s", len(BANNED_WORDS), sorted(BANNED_WORDS))


def _write_words() -> None:
    if _WORDS_FILE is None:
        return
    with _WORDS_FILE.open("w", encoding="utf-8") as f:
        for w in sorted(BANNED_WORDS):
            f.write(f"{w}\n")


def add_word(word: str) -> None:
    word = word.lower().strip()
    if not word:
        return
    if word not in BANNED_WORDS:
        BANNED_WORDS.add(word)
        _write_words()


def remove_word(word: str) -> None:
    word = word.lower().strip()
    if word in BANNED_WORDS:
        BANNED_WORDS.remove(word)
        _write_words()


def abuse_score(text: str, whitelist: Iterable[str] | None = None) -> int:
    """Return the number of banned words found in ``text``."""
    normalized = _normalize(text)
    tokens = normalized.split()

    ignored = {w.lower().strip() for w in whitelist} if whitelist else set()
    banned = BANNED_WORDS - ignored
    joined = " ".join(tokens)

    count = 0
    for word in banned:
        if " " in word:
            if word in joined:
                logger.debug("[ABUSE] Matched phrase: %s", word)
                count += 1
        else:
            if word in tokens:
                logger.debug("[ABUSE] Matched word: %s", word)
                count += 1
    return count


def contains_abuse(text: str, whitelist: Iterable[str] | None = None) -> bool:
    """Return ``True`` if ``text`` contains a banned word not in ``whitelist``."""
    return abuse_score(text, whitelist) > 0
