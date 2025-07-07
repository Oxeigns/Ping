import logging
from pyrogram import filters
from pyrogram.types import Message

logger = logging.getLogger(__name__)

from helpers import (
    catch_errors,
    get_or_create_user,
    is_admin,
    approve_user,
)
from config import Config


def register(app):
    @app.on_message(filters.command("broadcast") & filters.user(Config.OWNER_ID))
    @catch_errors
    async def broadcast_handler(client, message: Message):
        logger.info("/broadcast by %s", message.from_user.id)
        if len(message.command) < 2:
            await message.reply_text("⚠️ Usage:\n`/broadcast <message>`", quote=True)
            return

        text = message.text.split(None, 1)[1]
        await message.reply_text("📢 Broadcasting your message...")
        sent = 0
        async for dialog in app.get_dialogs():
            try:
                await app.send_message(dialog.chat.id, text)
                sent += 1
            except Exception:
                continue

        await message.reply_text(f"✅ Broadcast sent to `{sent}` chats.")

    @app.on_message(filters.command("approve"))
    @catch_errors
    async def approve_handler(client, message: Message):
        if not await is_admin(message):
            return
        if not message.reply_to_message:
            await message.reply_text("👤 Please reply to a user to approve them.")
            return

        user_id = message.reply_to_message.from_user.id
        await approve_user(app.db, user_id, True)
        await message.reply_text(f"✅ Approved [user](tg://user?id={user_id}).", disable_web_page_preview=True)
        logger.info("Approved user %s via %s", user_id, message.from_user.id)

    @app.on_message(filters.command("unapprove"))
    @catch_errors
    async def unapprove_handler(client, message: Message):
        if not await is_admin(message):
            return
        if not message.reply_to_message:
            await message.reply_text("👤 Please reply to a user to unapprove them.")
            return

        user_id = message.reply_to_message.from_user.id
        await approve_user(app.db, user_id, False)
        await message.reply_text(f"❌ Unapproved [user](tg://user?id={user_id}).", disable_web_page_preview=True)
        logger.info("Unapproved user %s via %s", user_id, message.from_user.id)

    @app.on_message(filters.command("approved"))
    @catch_errors
    async def approved_list(client, message: Message):
        if not await is_admin(message):
            return

        async with app.db.execute("SELECT id FROM users WHERE approved=1") as cur:
            rows = await cur.fetchall()

        if not rows:
            await message.reply_text("ℹ️ No users have been approved yet.")
            return

        lines = [f"- [user](tg://user?id={row[0]})" for row in rows]
        await message.reply_text("✅ **Approved Users:**\n" + "\n".join(lines), disable_web_page_preview=True)
        logger.info("Listed approved users for %s", message.from_user.id)

    @app.on_message(filters.command("rmwarn"))
    @catch_errors
    async def rmwarn_handler(client, message: Message):
        if not await is_admin(message):
            return
        if not message.reply_to_message:
            await message.reply_text("👤 Please reply to the user whose warnings you want to clear.")
            return

        user_id = message.reply_to_message.from_user.id
        await get_or_create_user(app.db, user_id)
        await app.db.execute("UPDATE users SET warnings=0 WHERE id=?", (user_id,))
        await app.db.commit()
        await message.reply_text(f"✅ Cleared all warnings for [user](tg://user?id={user_id}).", disable_web_page_preview=True)
        logger.info("Cleared warnings for %s via %s", user_id, message.from_user.id)
