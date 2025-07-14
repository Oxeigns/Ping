import logging
import asyncio
import re
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from googletrans import Translator
from helpers.abuse import contains_abuse, init_words

logger = logging.getLogger(__name__)

translator = Translator()


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
    if not text:
        return

    try:
        loop = asyncio.get_running_loop()
        translated = await loop.run_in_executor(
            None, translator.translate, text, "en"
        )
        check_text = translated.text
    except Exception as e:
        logger.debug("translation failed: %s", e)
        check_text = text

    if contains_abuse(check_text):
        try:
            await message.delete()
            logger.info("Deleted message from %s: %s", message.from_user.id, text)
        except Exception as e:
            logger.warning("failed to delete message: %s", e)


def register(app: Client):
    init_words()
    handler = MessageHandler(check_banned_words, filters.group)
    app.add_handler(handler)
    logger.info("✅ Moderation handler registered.")
