"""Utility helpers for safely formatting messages."""

import logging
import re
from helpers.compat import Client, Message
try:  # pragma: no cover - optional dependency
    from pyrogram.enums import ParseMode
except Exception:  # pragma: no cover - simple stub
    class ParseMode:
        MARKDOWN = "markdown"
        HTML = "html"
from config import Config

logger = logging.getLogger(__name__)

MD_V2_SPECIAL = re.compile(r"([_\*\[\]()~`>#+\-=|{}.!])")

def escape_markdown(text: str) -> str:
    """Escape Telegram MarkdownV2 special characters."""
    return MD_V2_SPECIAL.sub(r"\\\1", text)

async def safe_edit(message: Message, text: str, **kwargs) -> None:
    """Edit ``message`` with Markdown, falling back to HTML and plain text."""
    kwargs.pop("parse_mode", None)
    try:
        await message.edit_text(
            escape_markdown(text), parse_mode=ParseMode.MARKDOWN, **kwargs
        )
        return
    except Exception as e:
        logger.warning("Markdown edit failed: %s", e)
    try:
        await message.edit_text(text, parse_mode=ParseMode.HTML, **kwargs)
        return
    except Exception as e:
        logger.warning("HTML edit failed: %s", e)
    try:
        await message.edit_text(text, **kwargs)
    except Exception as e:
        logger.error("Plain edit failed: %s", e)


async def send_message_safe(target: Message | Client, text: str, **kwargs) -> Message:
    """Reply or send a message using Markdown -> HTML -> plain text."""
    kwargs.pop("parse_mode", None)
    reply_func = getattr(target, "reply", None)
    send_func = getattr(target, "send_message", None)

    try:
        formatted = escape_markdown(text)
        if reply_func:
            return await reply_func(formatted, parse_mode=ParseMode.MARKDOWN, **kwargs)
        return await send_func(formatted, parse_mode=ParseMode.MARKDOWN, **kwargs)
    except Exception as e:
        logger.debug("Markdown send failed: %s", e)
    try:
        if reply_func:
            return await reply_func(text, parse_mode=ParseMode.HTML, **kwargs)
        return await send_func(text, parse_mode=ParseMode.HTML, **kwargs)
    except Exception as e:
        logger.debug("HTML send failed: %s", e)
    if reply_func:
        return await reply_func(text, **kwargs)
    return await send_func(text, **kwargs)

