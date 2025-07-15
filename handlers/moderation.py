import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from googletrans import Translator

translator = Translator()
from helpers.mongo import get_db
from helpers.abuse import contains_abuse, abuse_score, init_words

logger = logging.getLogger(__name__)


async def check_banned_words(client: Client, message: Message):
    if not message.from_user or message.from_user.is_self:
        return

    db = get_db()
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
    except Exception as e:
        logger.debug("❌ Failed to fetch member status: %s", e)
        return

    raw_text = (message.text or message.caption or "").strip()
    if not raw_text:
        return
    text = raw_text.lower()

    # Translate message to English
    try:
        loop = asyncio.get_running_loop()
        translated = await loop.run_in_executor(
            None, lambda: translator.translate(raw_text, dest="en")
        )
        check_text = translated.text.lower()
    except Exception as e:
        logger.debug("❌ Translation failed: %s", e)
        check_text = text

    # Load whitelist
    settings = await db.group_settings.find_one({"chat_id": message.chat.id}) or {}
    whitelist = settings.get("whitelist", [])

    threshold = settings.get("abuse_threshold", 1)

    score = max(
        abuse_score(check_text, whitelist),
        abuse_score(text, whitelist),
    )
    abuse = score >= threshold or contains_abuse(check_text, whitelist) or contains_abuse(text, whitelist)
    logger.debug("Abuse check %s | score=%s | text='%s' | translated='%s'", abuse, score, text, check_text)
    if abuse:
        if member.status not in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}:
            logger.debug("Attempting to delete message from %s", message.from_user.id)
            try:
                await message.delete()
                logger.info("🗑 Deleted abusive message from %s: %s", message.from_user.id, text)
            except Exception as e:
                logger.warning("❌ Failed to delete abusive message: %s", e)
        else:
            logger.debug("Skipping deletion for admin %s", message.from_user.id)

        if member.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}:
            warn = f"⚠️ Admin {message.from_user.mention}, kindly avoid using banned words."
        else:
            warn = f"⚠️ {message.from_user.mention}, please avoid using banned words."

        try:
            await client.send_message(message.chat.id, warn)
        except Exception as e:
            logger.debug("❌ Failed to send warning: %s", e)


def register(app: Client):
    init_words()
    handler = MessageHandler(check_banned_words, filters.group)
    app.add_handler(handler)
    logger.info("✅ Abuse filter handler registered.")
