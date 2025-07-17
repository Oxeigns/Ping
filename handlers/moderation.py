import asyncio
import logging
import re
from helpers.compat import Client, Message, Translator, ChatMemberStatus, filters
from helpers import get_state, require_admin, send_message_safe
import texts
from helpers.abuse import BANNED_WORDS, abuse_score, init_words
from database import add_log, get_or_create_user, is_approved
from config import Config

# --- INITIALIZATION ----------------------------------------------------------

init_words()
logger = logging.getLogger(__name__)
translator = Translator()
_THREAD_POOL = None

# Pre‐compile a regex to detect any banned word in O(1) per message
BANNED_REGEX = re.compile(
    r'\b(' + '|'.join(re.escape(w) for w in BANNED_WORDS) + r')\b',
    flags=re.IGNORECASE
)


def _get_thread_pool():
    global _THREAD_POOL
    if _THREAD_POOL is None:
        _THREAD_POOL = asyncio.get_running_loop()
    return _THREAD_POOL


async def safe_translate(text: str) -> str:
    try:
        # Offload blocking translate call to default executor
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, translator.translate, text, "en")
        return getattr(result, "text", text)
    except Exception as exc:
        logger.debug("translate failed: %s", exc)
        return text


async def process_violation(client: Client, message: Message, reason: str) -> None:
    user = message.from_user
    user_id = user.id if user else 0
    chat = message.chat
    chat_title = getattr(chat, "title", None) or chat.id

    # Log deletion
    logger.warning("❌ Deleted from %s in %s (%s)", user_id, chat_title, reason)
    await add_log(client.db, user_id, chat.id, "abuse", 1.0)
    await send_message_safe(chat, texts.ABUSE_WARNING)

    if Config.MODLOG_CHANNEL:
        msg_type = "photo" if message.photo else "video" if message.video else "text"
        log_text = f"❌ Deleted {msg_type} from {user_id} in {chat_title} – {reason}"
        try:
            await client.send_message(Config.MODLOG_CHANNEL, log_text)
        except Exception as exc:
            logger.debug("modlog failed: %s", exc)


# --- HANDLER REGISTRATION ----------------------------------------------------

def register(app: Client):
    @app.on_message(filters.command("off_text_delete") & filters.group)
    @require_admin
    async def toggle_text(_, message: Message):
        state = get_state(message.chat.id)
        state.text_filter = not state.text_filter
        await message.reply_text(f"🛑 Text filter {'disabled' if not state.text_filter else 'enabled'}.")

    @app.on_message(filters.command("off_media_delete") & filters.group)
    @require_admin
    async def toggle_media(_, message: Message):
        state = get_state(message.chat.id)
        state.media_filter = not state.media_filter
        await message.reply_text(f"🛑 Media filter {'disabled' if not state.media_filter else 'enabled'}.")

    @app.on_message(filters.command("status") & filters.group)
    async def status(_, message: Message):
        s = get_state(message.chat.id)
        text = (
            f"🛡 Text filter: {'ON' if s.text_filter else 'OFF'}\n"
            f"📷 Media filter: {'ON' if s.media_filter else 'OFF'}\n"
            f"🚫 Banned users: {len(s.banned_users)}"
        )
        await message.reply_text(text)

    @app.on_message(filters.command("banlist") & filters.group)
    async def banlist(_, message: Message):
        s = get_state(message.chat.id)
        if not s.banned_users:
            return await message.reply_text("✅ No banned users.")
        users = "\n".join(str(u) for u in s.banned_users)
        await message.reply_text(f"🚫 Banned users:\n{users}")

    @app.on_message(filters.command("unban") & filters.group)
    @require_admin
    async def unban(_, message: Message):
        cmd = message.command
        if len(cmd) < 2 or not cmd[1].isdigit():
            return await message.reply_text("Usage: /unban <user_id>")
        uid = int(cmd[1])
        state = get_state(message.chat.id)
        if uid in state.banned_users:
            state.banned_users.remove(uid)
            await message.reply_text("✅ User unbanned.")
        else:
            await message.reply_text("ℹ️ User not in ban list.")

    @app.on_message(filters.group & (filters.text | filters.caption))
    async def check_message(client: Client, message: Message):
        s = get_state(message.chat.id)
        text = message.text or message.caption or ""
        # Skip if filter disabled
        if (message.text and not s.text_filter) or (message.caption and not s.media_filter):
            return

        user = message.from_user
        if not text or (user and user.id in {Config.OWNER_ID}):
            return
        # Skip approved users
        if user and await is_approved(client.db, user.id):
            return
        await get_or_create_user(client.db, user.id)

        # Translate once
        scan_text = await safe_translate(text)

        # Fast regex check
        if not BANNED_REGEX.search(scan_text):
            return

        # Confirm non-admin
        member = await client.get_chat_member(message.chat.id, user.id)
        if member.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}:
            return

        # Delete & warn
        try:
            await message.delete()
        except Exception as exc:
            logger.debug("delete failed: %s", exc)

        await process_violation(client, message, "abusive content")
