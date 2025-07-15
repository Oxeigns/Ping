import logging
import asyncio
import re
from pathlib import Path
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from googletrans import Translator
from helpers.mongo import get_db

logger = logging.getLogger(__name__)

translator = Translator()

# Load banned words from banned_words.txt
BANNED_WORDS_FILE = Path("banned_words.txt")  # ensure correct path
banned_words = []

def load_banned_words():
    global banned_words
    if BANNED_WORDS_FILE.exists():
        with open(BANNED_WORDS_FILE, "r", encoding="utf-8") as f:
            banned_words = [line.strip().lower() for line in f if line.strip()]
        logger.info(f"✅ Loaded {len(banned_words)} banned words from file.")
    else:
        logger.warning("⚠️ banned_words.txt file not found.")

def contains_abuse(text: str, whitelist: list) -> bool:
    cleaned_text = re.sub(r"[^\w\s]", "", text).lower()
    for word in banned_words:
        if word in whitelist:
            continue
        if re.search(rf"\b{re.escape(word)}\b", cleaned_text):
            return True
    return False

async def check_banned_words(client: Client, message: Message):
    if not message.from_user or message.from_user.is_self:
        return

    db = get_db()
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
    except Exception as e:
        logger.debug("❌ Failed to fetch member status: %s", e)
        return

    text = message.text or message.caption or ""
    if not text:
        return

    # Translate message to English
    try:
        loop = asyncio.get_running_loop()
        translated = await loop.run_in_executor(
            None, lambda: translator.translate(text, dest="en")
        )
        check_text = translated.text
    except Exception as e:
        logger.debug("❌ Translation failed: %s", e)
        check_text = text

    # Load whitelist
    settings = await db.group_settings.find_one({"chat_id": message.chat.id}) or {}
    whitelist = settings.get("whitelist", [])

    if contains_abuse(check_text, whitelist):
        try:
            await message.delete()
            logger.info("🗑 Deleted abusive message from %s: %s", message.from_user.id, text)
        except Exception as e:
            logger.warning("❌ Failed to delete abusive message: %s", e)

        if member.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}:
            warn = f"⚠️ Admin {message.from_user.mention}, kindly avoid using banned words."
        else:
            warn = f"⚠️ {message.from_user.mention}, please avoid using banned words."

        try:
            await client.send_message(message.chat.id, warn)
        except Exception as e:
            logger.debug("❌ Failed to send warning: %s", e)

def register(app: Client):
    load_banned_words()
    handler = MessageHandler(check_banned_words, filters.group)
    app.add_handler(handler)
    logger.info("✅ Abuse filter handler registered.")
