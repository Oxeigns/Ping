from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus

from helpers.text_filter import load_banned_words, contains_banned_word
from helpers import require_admin, send_message_safe, get_state

BANNED_WORDS = load_banned_words()


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
        if contains_banned_word(text, BANNED_WORDS):
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            if member.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}:
                await send_message_safe(message, "⚠️ Dear admin, please avoid restricted terms.")
            else:
                try:
                    await message.delete()
                except Exception:
                    pass
                await send_message_safe(message, "❌ Your message contained banned content. Continued abuse may result in action.")
                state.banned_users.add(message.from_user.id)
