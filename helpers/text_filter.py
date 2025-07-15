from pathlib import Path
from typing import Set


def load_banned_words(path: str = "banned_words.txt") -> Set[str]:
    """Load banned words from a text file.

    Parameters
    ----------
    path: str, optional
        Path to the banned words file. By default ``banned_words.txt`` in the
        same directory as this module.

    Returns
    -------
    Set[str]
        A set containing the banned words in lowercase. If the file is not
        found, an empty set is returned.
    """
    p = Path(path)
    if not p.is_absolute():
        # Resolve relative paths from the project root rather than this module's
        # directory so ``banned_words.txt`` placed beside ``run.py`` is found
        # regardless of the current working directory.
        p = Path(__file__).resolve().parent.parent / path

    try:
        with p.open("r", encoding="utf-8") as f:
            return {line.strip().lower() for line in f if line.strip()}
    except FileNotFoundError:
        return set()


def contains_banned_word(text: str, banned_words: Set[str]) -> bool:
    """Check if the given text contains any banned word.

    Matching is case-insensitive and substring-based.

    Parameters
    ----------
    text: str
        The text to scan.
    banned_words: Set[str]
        A set of banned words, typically produced by :func:`load_banned_words`.

    Returns
    -------
    bool
        ``True`` if any banned word is present in ``text``.
    """
    lower_text = text.lower()
    return any(word in lower_text for word in banned_words)
