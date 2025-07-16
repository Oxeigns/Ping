import asyncio
import logging
from googletrans import Translator
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message

from helpers import get_state, require_admin, send_message_safe
from helpers.abuse import BANNED_WORDS, abuse_score, init_words
from database import add_warning, add_log, get_or_create_user, is_approved
from config import Config

init_words()
logger = logging.getLogger(__name__)
translator = Translator()
WARN_THRESHOLD = 3


async def process_violation(client: Client, message: Message, score: float) -> None:
    user_id = message.from_user.id if message.from_user else 0
    logger.warning("violation by %s score %.2f", user_id, score)
    db = client.db
    await add_log(db, user_id, message.chat.id, "abuse", score)
    user = await add_warning(db, user_id, score)
    if user["warnings"] >= WARN_THRESHOLD:
        try:
            await client.restrict_chat_member(message.chat.id, user_id, permissions={})
        except Exception as exc:
            logger.error("restrict failed: %s", exc)
        await client.send_message(
            message.chat.id, "🔇 User muted for repeated violations."
        )
    else:
        await client.send_message(
            message.chat.id, f"⚠️ Warning {user['warnings']} issued."
        )
    if Config.MODLOG_CHANNEL:
        try:
            await client.send_message(
                Config.MODLOG_CHANNEL,
                f"Violation in {message.chat.id} by {user_id} score {score:.2f}",
            )
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

    @app.on_message(filters.command("help") & (filters.group | filters.private))
    async def help_cmd(_, message: Message):
        text = (
            "Available commands:\n"
            "/off_text_delete - toggle text filter\n"
            "/off_media_delete - toggle media filter\n"
            "/status - show current status\n"
            "/banlist - list banned users\n"
            "/unban <user_id> - unban a user"
        )
        await message.reply_text(text)

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
        ratio = score / max(len(scan_text.split()), 1)
        if ratio == 0:
            return

        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}:
            await send_message_safe(
                message, "⚠️ Dear admin, please avoid restricted terms."
            )
            return

        try:
            await message.delete()
        except Exception as exc:
            logger.debug("delete failed: %s", exc)

        await process_violation(client, message, ratio)
