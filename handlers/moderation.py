import logging
import asyncio
from difflib import SequenceMatcher
from typing import Iterable, Tuple, Optional

from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from googletrans import Translator

from helpers.mongo import get_db
from helpers.abuse import load_words
from config import Config

BANNED_WORDS = load_words()
logger.info("Loaded %d banned words", len(BANNED_WORDS))

_CATEGORY_EXTRA = {
    "nsfw": {"porn", "sex"},
    "spam": {"scam", "carding", "hacking", "drugs"},
}

WORD_CATEGORY = {word: "abuse" for word in BANNED_WORDS}
for cat, words in _CATEGORY_EXTRA.items():
    for w in words:
        WORD_CATEGORY[w] = cat
        BANNED_WORDS.add(w)

logger = logging.getLogger(__name__)


def translate_text(text: str) -> str:
    """Translate ``text`` to English in a worker thread."""
    try:
        translator = Translator()
        translated = translator.translate(text, dest="en")
        return translated.text.lower()
    except Exception as exc:  # pragma: no cover - network call
        logger.debug("translation failed: %s", exc)
        return text.lower()


def detect_violation(text: str, whitelist: Iterable[str]) -> Optional[Tuple[str, str]]:
    """Return (category, word) if ``text`` contains a banned word."""
    tokens = text.lower().split()
    banned = BANNED_WORDS - set(w.lower() for w in whitelist)

    for token in tokens:
        if token in banned:
            return WORD_CATEGORY.get(token, "abuse"), token
        for word in banned:
            if len(word) > 3 and SequenceMatcher(None, token, word).ratio() >= 0.85:
                return WORD_CATEGORY.get(word, "abuse"), word

    joined = " ".join(tokens)
    for word in banned:
        if " " in word and word in joined:
            return WORD_CATEGORY.get(word, "abuse"), word
    return None


async def check_banned_words(client: Client, message: Message):
    if not message.from_user or message.from_user.is_self:
        return

    db = get_db()
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
    except Exception as e:
        logger.debug("Failed to fetch member status: %s", e)
        return

    raw_text = (message.text or message.caption or "").strip()
    if not raw_text:
        return

    text = raw_text.lower()

    # Translate in executor to avoid blocking event loop
    try:
        loop = asyncio.get_running_loop()
        check_text = await loop.run_in_executor(None, translate_text, raw_text)
    except Exception as e:
        logger.debug("❌ Async translation wrapper failed: %s", e)
        check_text = text

    settings = await db.group_settings.find_one({"chat_id": message.chat.id}) or {}
    if not settings.get("filter_enabled", True):
        return
    whitelist = settings.get("whitelist", [])

    violation = detect_violation(check_text, whitelist) or detect_violation(text, whitelist)

    if violation:
        category, word = violation
        is_group_admin = member.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}
        try:
            await message.delete()
        except Exception as exc:
            logger.debug("Failed to delete offending message: %s", exc)

        warn_admin = f"⚠️ {message.from_user.mention}, please avoid {category} terms."
        warn_user = f"❌ {message.from_user.mention}, {category} content is not allowed."
        warn_text = warn_admin if is_group_admin else warn_user

        try:
            await client.send_message(message.chat.id, warn_text)
        except Exception as e:
            logger.debug("Group warning failed: %s", e)
            try:
                await client.send_message(message.from_user.id, warn_text)
            except Exception as ex:
                logger.debug("DM warning failed: %s", ex)

        if Config.MODLOG_CHANNEL:
            try:
                log = (
                    f"User: <code>{message.from_user.id}</code>\n"
                    f"Chat: <code>{message.chat.id}</code>\n"
                    f"Category: {category}\nWord: {word}"
                )
                await client.send_message(Config.MODLOG_CHANNEL, log)
            except Exception as exc:
                logger.debug("Failed to send modlog: %s", exc)


def register(app: Client):
    logger.info("✅ Banned words initialized.")
    handler = MessageHandler(check_banned_words, filters.group & (filters.text | filters.caption))
    app.add_handler(handler)
    logger.info("✅ Abuse filter handler registered.")
