from pyrogram import filters
from pyrogram.types import Message

from config import Config
from utils import db, perms, errors, logger


def register(app):
    @app.on_message(filters.command("approve") & filters.group)
    @errors.catch_errors
    async def approve(client, message: Message):
        if not await perms.is_admin(message):
            return
        if not message.reply_to_message:
            await message.reply_text("Reply to a user to approve.")
            return
        user_id = message.reply_to_message.from_user.id
        await db.set_approved(app.db, message.chat.id, user_id, True)
        await message.reply_text("User approved")
        await logger.log_action(app, f"Approved {user_id} in {message.chat.id}")

    @app.on_message(filters.command("unapprove") & filters.group)
    @errors.catch_errors
    async def unapprove(client, message: Message):
        if not await perms.is_admin(message):
            return
        if not message.reply_to_message:
            await message.reply_text("Reply to a user to unapprove.")
            return
        user_id = message.reply_to_message.from_user.id
        await db.set_approved(app.db, message.chat.id, user_id, False)
        await message.reply_text("User unapproved")
        await logger.log_action(app, f"Unapproved {user_id} in {message.chat.id}")

    @app.on_message(filters.command("approved") & filters.group)
    @errors.catch_errors
    async def list_approved(client, message: Message):
        if not await perms.is_admin(message):
            return
        users = await db.list_approved(app.db, message.chat.id)
        text = "Approved users:\n" + "\n".join(str(u) for u in users)
        await message.reply_text(text or "No approved users")

