"""Manage abuse word list stored in ``banned_words.txt``."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Set, Iterable

logger = logging.getLogger(__name__)

BANNED_WORDS: Set[str] = set()
_WORDS_FILE: Path | None = None


def load_words(path: str = "banned_words.txt") -> Set[str]:
    """Load words from ``path`` into a set.

    Relative paths are resolved from the project root so the function works
    regardless of the current working directory.
    """
    p = Path(path)
    if not p.is_absolute():
        # ``helpers`` lives one level below the project root
        root = Path(__file__).resolve().parents[1]
        p = root / path
    if not p.exists():
        logger.warning("banned words file not found: %s", p)
        return set()
    with p.open("r", encoding="utf-8") as f:
        return {line.strip().lower() for line in f if line.strip()}


def init_words(path: str = "banned_words.txt") -> None:
    """Initialize the global word set from file."""
    global BANNED_WORDS, _WORDS_FILE
    _WORDS_FILE = Path(path)
    if not _WORDS_FILE.is_absolute():
        _WORDS_FILE = Path(__file__).resolve().parent.parent / path
    BANNED_WORDS = load_words(_WORDS_FILE)
    logger.info("loaded %d banned words from %s", len(BANNED_WORDS), _WORDS_FILE)


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
    """Return the number of banned words found in ``text``.

    The check is case-insensitive and counts each occurrence of a banned
    word that is not whitelisted.
    """
    if whitelist:
        ignored = {w.lower().strip() for w in whitelist}
    else:
        ignored = set()

    banned = BANNED_WORDS - ignored
    lower_text = text.lower()
    return sum(lower_text.count(word) for word in banned)


def contains_abuse(text: str, whitelist: Iterable[str] | None = None) -> bool:
    """Return ``True`` if ``text`` contains a banned word not in ``whitelist``."""
    return abuse_score(text, whitelist) > 0
