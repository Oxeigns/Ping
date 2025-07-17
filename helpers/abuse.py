"""Abusive word detection utilities for scanning messages."""

from __future__ import annotations

import logging
import os
import string
from pathlib import Path
from typing import Iterable, Set

logger = logging.getLogger(__name__)

BANNED_WORDS: Set[str] = set()
_WORDS_FILE: Path | None = None

# Map all punctuation to space to prevent "h@te" bypasses
_PUNCT_TABLE = str.maketrans({p: " " for p in string.punctuation})


def _normalize(text: str) -> str:
    """Lowercase text and replace punctuation with spaces."""
    return text.lower().translate(_PUNCT_TABLE)


def _resolve_path(path: str) -> Path:
    """Return an absolute path for `path` relative to project root."""
    p = Path(path)
    if not p.is_absolute():
        p = Path(__file__).resolve().parents[1] / path
    return p


def load_words(path: str = "banned_words.txt") -> Set[str]:
    """Load banned words from file and return as a lowercase set."""
    p = _resolve_path(path)
    if not p.exists():
        raise FileNotFoundError(f"[ABUSE] banned_words.txt not found at {p}")
    with p.open("r", encoding="utf-8") as f:
        words = {line.strip().lower() for line in f if line.strip()}
    logger.debug("[ABUSE] Loaded %d banned words from %s", len(words), p)
    return words


def init_words(path: str = "banned_words.txt") -> None:
    """Initialize the global `BANNED_WORDS` set from file."""
    global BANNED_WORDS, _WORDS_FILE
    _WORDS_FILE = _resolve_path(path)
    BANNED_WORDS = load_words(_WORDS_FILE)
    logger.info("[ABUSE] Initialized banned words (%d): %s", len(BANNED_WORDS), sorted(BANNED_WORDS))


def _write_words() -> None:
    """Write the current BANNED_WORDS set back to file."""
    if _WORDS_FILE is None:
        return
    with _WORDS_FILE.open("w", encoding="utf-8") as f:
        for w in sorted(BANNED_WORDS):
            f.write(f"{w}\n")


def add_word(word: str) -> None:
    """Add a word to the banned list and save it."""
    word = word.strip().lower()
    if word and word not in BANNED_WORDS:
        BANNED_WORDS.add(word)
        _write_words()
        logger.info("[ABUSE] Added word: %s", word)


def remove_word(word: str) -> None:
    """Remove a word from the banned list and save."""
    word = word.strip().lower()
    if word in BANNED_WORDS:
        BANNED_WORDS.remove(word)
        _write_words()
        logger.info("[ABUSE] Removed word: %s", word)


def abuse_score(text: str, whitelist: Iterable[str] | None = None) -> int:
    """
    Return number of banned words found in text, excluding any from whitelist.
    - Matches individual words and phrases (multi-word strings).
    - Case-insensitive, normalized.
    """
    if not BANNED_WORDS:
        return 0

    normalized = _normalize(text)
    tokens = normalized.split()
    token_set = set(tokens)
    joined = " ".join(tokens)

    ignored = {w.strip().lower() for w in whitelist} if whitelist else set()
    active_banned = BANNED_WORDS - ignored

    score = 0
    for word in active_banned:
        if " " in word:
            if word in joined:
                logger.debug("[ABUSE] Matched phrase: %s", word)
                score += 1
        else:
            if word in token_set:
                logger.debug("[ABUSE] Matched word: %s", word)
                score += 1
    return score


def contains_abuse(text: str, whitelist: Iterable[str] | None = None) -> bool:
    """Returns True if abusive word/phrase exists in text."""
    return abuse_score(text, whitelist) > 0
