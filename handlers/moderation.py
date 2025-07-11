import logging
import re
from pathlib import Path
from typing import Set

from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus

logger = logging.getLogger(__name__)

BANNED_WORDS: Set[str] = set()


def load_banned_words(path: str = "banned_words.txt") -> Set[str]:
    p = Path(__file__).resolve().parent.parent / path
    try:
        with p.open("r", encoding="utf-8") as f:
            return {line.strip().lower() for line in f if line.strip()}
    except FileNotFoundError:
        logger.warning("banned words file not found: %s", p)
        return set()


async def check_banned_words(client: Client, message: Message):
    if not message.from_user or message.from_user.is_self:
        return

    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in {ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR}:
            return
    except Exception as e:
        logger.debug("failed to fetch member status: %s", e)
        return

    text = message.text or message.caption or ""
    tokens = re.findall(r"\w+", text.lower())
    if any(token in BANNED_WORDS for token in tokens):
        try:
            await message.delete()
            logger.info("Deleted message from %s: %s", message.from_user.id, text)
        except Exception as e:
            logger.warning("failed to delete message: %s", e)


def register(app: Client):
    global BANNED_WORDS
    BANNED_WORDS = load_banned_words()
    handler = MessageHandler(check_banned_words, filters.text & filters.group)
    app.add_handler(handler)
    logger.info("✅ Moderation handler registered.")
