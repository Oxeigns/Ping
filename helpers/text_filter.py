import re
from pathlib import Path
from typing import Set


def load_banned_words(path: str = "banned_words.txt") -> Set[str]:
    """
    Load banned words from a text file.

    Parameters
    ----------
    path : str
        Path to the banned words file (relative or absolute).

    Returns
    -------
    Set[str]
        A set of banned words (lowercased).
    """
    p = Path(path)

    if not p.is_absolute():
        # Resolve from project root if relative
        p = Path(__file__).resolve().parent.parent / path

    try:
        with p.open("r", encoding="utf-8") as f:
            return {line.strip().lower() for line in f if line.strip()}
    except FileNotFoundError:
        return set()


def contains_banned_word(text: str, banned_words: Set[str]) -> bool:
    """
    Check if the given text contains any banned word using regex.

    Parameters
    ----------
    text : str
        The text to check.
    banned_words : Set[str]
        The set of words to look for.

    Returns
    -------
    bool
        True if any banned word is found; otherwise False.
    """
    if not banned_words:
        return False

    pattern = build_regex_from_words(banned_words)
    return bool(pattern.search(text))


def build_regex_from_words(words: Set[str]) -> re.Pattern:
    """
    Build a safe regex pattern that matches any of the given words as whole words.

    Parameters
    ----------
    words : Set[str]
        Words to match.

    Returns
    -------
    re.Pattern
        Compiled regex object for matching.
    """
    escaped = [re.escape(w) for w in words]
    pattern = r"\b(" + "|".join(escaped) + r")\b"
    return re.compile(pattern, re.IGNORECASE)
