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
    """Edit a message using MarkdownV2 and fall back to HTML on failure."""
    try:
        await message.edit_text(
            escape_markdown(text), parse_mode="MarkdownV2", **kwargs
        )
    except Exception as e:
        logger.warning("❗ Failed to edit message %s: %s", message.id, e)
        await message.edit_text(text, parse_mode="HTML", **kwargs)


async def send_message_safe(target: Message | Client, text: str, **kwargs) -> Message:
    """Reply or send a message safely using MarkdownV2, fall back to HTML."""
    reply_func = getattr(target, "reply", None)
    send_func = getattr(target, "send_message", None)

    try:
        formatted = escape_markdown(text)
        if reply_func:
            return await reply_func(formatted, parse_mode="MarkdownV2", **kwargs)
        return await send_func(formatted, parse_mode="MarkdownV2", **kwargs)
    except Exception as e:
        logger.debug("Markdown failed: %s", e)
        if reply_func:
            return await reply_func(text, parse_mode="HTML", **kwargs)
        return await send_func(text, parse_mode="HTML", **kwargs)

