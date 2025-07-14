"""Utility helpers for safely formatting messages."""

import logging
import re
from pyrogram import Client
from pyrogram.types import Message

logger = logging.getLogger(__name__)

MD_V2_SPECIAL = re.compile(r"([_\*\[\]()~`>#+\-=|{}.!])")

def escape_markdown(text: str) -> str:
    """Escape Telegram MarkdownV2 special characters."""
    return MD_V2_SPECIAL.sub(r"\\\1", text)

async def safe_edit(message: Message, text: str, **kwargs) -> None:
    """Edit a message trying MarkdownV2, then HTML, then plain text."""
    try:
        await message.edit_text(
            escape_markdown(text), parse_mode="MarkdownV2", **kwargs
        )
        return
    except Exception as e:
        logger.warning("Markdown edit failed: %s", e)
    try:
        await message.edit_text(text, parse_mode="HTML", **kwargs)
        return
    except Exception as e:
        logger.warning("HTML edit failed: %s", e)
    await message.edit_text(text, **kwargs)


async def send_message_safe(target: Message | Client, text: str, **kwargs) -> Message:
    """Reply or send a message using MarkdownV2 -> HTML -> plain text."""
    reply_func = getattr(target, "reply", None)
    send_func = getattr(target, "send_message", None)

    try:
        formatted = escape_markdown(text)
        if reply_func:
            return await reply_func(formatted, parse_mode="MarkdownV2", **kwargs)
        return await send_func(formatted, parse_mode="MarkdownV2", **kwargs)
    except Exception as e:
        logger.debug("Markdown send failed: %s", e)
    try:
        if reply_func:
            return await reply_func(text, parse_mode="HTML", **kwargs)
        return await send_func(text, parse_mode="HTML", **kwargs)
    except Exception as e:
        logger.debug("HTML send failed: %s", e)
    if reply_func:
        return await reply_func(text, **kwargs)
    return await send_func(text, **kwargs)

