"""Fallback definitions for optional third-party packages.

This module provides minimal stand-ins for classes from external
dependencies so that the rest of the codebase can be imported without
those packages installed. The stubs only implement the attributes used
in the test suite and raise no errors when accessed.
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Pyrogram stubs
# ---------------------------------------------------------------------------

try:  # pragma: no cover - only executed when pyrogram is available
    from pyrogram import Client, filters  # type: ignore
    from pyrogram.types import CallbackQuery, Message  # type: ignore
    from pyrogram.errors import UserIsBlocked  # type: ignore
    from pyrogram.enums import ChatMemberStatus  # type: ignore
    PYROGRAM_AVAILABLE = True
except Exception:  # pragma: no cover - pyrogram missing
    PYROGRAM_AVAILABLE = False

    class Client:  # pragma: no cover - simple stub
        pass

    class _Filter:
        def __call__(self, *args: Any, **kwargs: Any) -> "_Filter":
            return self

        def __and__(self, other: Any) -> "_Filter":
            return self

        __rand__ = __and__

        def __or__(self, other: Any) -> "_Filter":
            return self

        __ror__ = __or__

        def __invert__(self) -> "_Filter":
            return self

    class _Filters:  # pragma: no cover - provides filter factories
        def __getattr__(self, name: str) -> _Filter:
            return _Filter()

        def __call__(self, *args: Any, **kwargs: Any) -> _Filter:
            return _Filter()

    filters = _Filters()

    class Message:  # pragma: no cover - minimal stand in
        pass

    class CallbackQuery:  # pragma: no cover - minimal stand in
        pass

    class UserIsBlocked(Exception):  # pragma: no cover
        pass

    class ChatMemberStatus:  # pragma: no cover - enum constants used in code
        ADMINISTRATOR = "administrator"
        OWNER = "owner"


# ---------------------------------------------------------------------------
# googletrans stubs
# ---------------------------------------------------------------------------

try:  # pragma: no cover
    from googletrans import Translator  # type: ignore
    GOOGLETRANS_AVAILABLE = True
except Exception:  # pragma: no cover - googletrans missing
    GOOGLETRANS_AVAILABLE = False

    class Translator:  # pragma: no cover - basic translate mock
        def translate(self, text: str, dest: str) -> Any:
            return type("Translation", (), {"text": text})


__all__ = [
    "Client",
    "filters",
    "Message",
    "CallbackQuery",
    "UserIsBlocked",
    "ChatMemberStatus",
    "Translator",
    "PYROGRAM_AVAILABLE",
    "GOOGLETRANS_AVAILABLE",
]

