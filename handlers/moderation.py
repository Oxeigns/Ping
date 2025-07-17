import asyncio
import logging
from helpers.compat import (
    Client,
    Message,
    Translator,
    ChatMemberStatus,
    filters,
)

from helpers import get_state, require_admin, send_message_safe
import texts
from helpers.abuse import BANNED_WORDS, abuse_score, init_words
from database import add_log, get_or_create_user, is_approved
from config import Config

init_words()
logger = logging.getLogger(__name__)
translator = Translator()
async def process_violation(client: Client, message: Message, reason: str) -> None:
    user = message.from_user
    user_id = user.id if user else 0
    chat_title = message.chat.title or message.chat.id
    logger.warning("\u274C deleted message from %s in %s (%s)", user_id, chat_title, reason)
    db = client.db
    await add_log(db, user_id, message.chat.id, "abuse", 1.0)
    await send_message_safe(message.chat, texts.ABUSE_WARNING)
    if Config.MODLOG_CHANNEL:
        msg_type = "photo" if message.photo else "video" if message.video else "text"
        log = f"❌ Deleted {msg_type} from {user_id} in {chat_title} - {reason}"
        try:
            await client.send_message(Config.MODLOG_CHANNEL, log)
        except Exception as exc:
            logger.debug("modlog failed: %s", exc)


def register(app: Client):
    @app.on_message(filters.command("off_text_delete") & filters.group)
    @require_admin
    async def toggle_text(_, message: Message):
        state = get_state(message.chat.id)
        state.text_filter = not state.text_filter
        status = "disabled" if not state.text_filter else "enabled"
        await message.reply_text(f"Text filter {status}.")

    @app.on_message(filters.command("off_media_delete") & filters.group)
    @require_admin
    async def toggle_media(_, message: Message):
        state = get_state(message.chat.id)
        state.media_filter = not state.media_filter
        status = "disabled" if not state.media_filter else "enabled"
        await message.reply_text(f"Media filter {status}.")

    @app.on_message(filters.command("status") & filters.group)
    async def status(_, message: Message):
        s = get_state(message.chat.id)
        text = (
            f"Text filter: {'ON' if s.text_filter else 'OFF'}\n"
            f"Media filter: {'ON' if s.media_filter else 'OFF'}\n"
            f"Banned users: {len(s.banned_users)}"
        )
        await message.reply_text(text)

    @app.on_message(filters.command("banlist") & filters.group)
    async def banlist(_, message: Message):
        s = get_state(message.chat.id)
        if not s.banned_users:
            await message.reply_text("No banned users.")
        else:
            users = "\n".join(str(u) for u in s.banned_users)
            await message.reply_text(f"Banned users:\n{users}")

    @app.on_message(filters.command("unban") & filters.group)
    @require_admin
    async def unban(_, message: Message):
        if len(message.command) < 2:
            await message.reply_text("Usage: /unban <user_id>")
            return
        try:
            uid = int(message.command[1])
        except ValueError:
            await message.reply_text("Invalid user id")
            return
        state = get_state(message.chat.id)
        if uid in state.banned_users:
            state.banned_users.remove(uid)
            await message.reply_text("User unbanned")
        else:
            await message.reply_text("User not in ban list")


    @app.on_message(filters.group & (filters.text | filters.caption))
    async def check_message(client: Client, message: Message):
        state = get_state(message.chat.id)
        text = message.text or message.caption or ""
        if message.text and not state.text_filter:
            return
        if message.caption and not state.media_filter:
            return
        if not text:
            return

        if message.from_user and message.from_user.id == Config.OWNER_ID:
            return
        if await is_approved(client.db, message.from_user.id):
            return
        await get_or_create_user(client.db, message.from_user.id)

        loop = asyncio.get_running_loop()
        try:
            translation = await loop.run_in_executor(
                None, translator.translate, text, "en"
            )
            scan_text = translation.text
        except Exception as exc:
            logger.debug("translate failed: %s", exc)
            scan_text = text

        score = abuse_score(scan_text)
        if score == 0:
            return

        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}:
            return

        try:
            await message.delete()
        except Exception as exc:
            logger.debug("delete failed: %s", exc)

        await process_violation(client, message, "abusive content")
