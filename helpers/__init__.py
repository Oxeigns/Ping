"""
Helper modules for the bot.
This module aggregates commonly used functions and utilities for easy access.
"""

from database import (
    get_or_create_user,
    add_warning,
    approve_user,
    add_log,
    upsert_group,
    remove_group,
)

from .api import (
    check_toxicity,
    check_image,
)

from .perms import (
    is_admin,
    is_owner,
)

from .decorators import catch_errors
from .formatting import safe_edit

__all__ = [
    "get_or_create_user",
    "add_warning",
    "approve_user",
    "add_log",
    "upsert_group",
    "remove_group",
    "check_toxicity",
    "check_image",
    "is_admin",
    "is_owner",
    "catch_errors",
    "safe_edit",
]
