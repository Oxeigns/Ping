from pyrogram import filters
from pyrogram.types import Message

from utils import catch_errors, is_owner, get_or_create_user, is_admin
from config import Config


def register(app):
    @app.on_message(filters.command("broadcast") & filters.user(Config.OWNER_ID))
    @catch_errors
    async def broadcast_handler(client, message: Message):
        if len(message.command) < 2:
            await message.reply_text("Usage: /broadcast <text>")
            return
        text = message.text.split(None, 1)[1]
        await message.reply_text("Broadcasting...")
        sent = 0
        async for dialog in app.get_dialogs():
            try:
                await app.send_message(dialog.chat.id, text)
                sent += 1
            except Exception:
                continue
        await message.reply_text(f"Broadcast sent to {sent} chats.")

    @app.on_message(filters.command("approve"))
    @catch_errors
    async def approve_handler(client, message: Message):
        if not await is_admin(message):
            return
        if not message.reply_to_message:
            await message.reply_text("Reply to a user to approve.")
            return
        user_id = message.reply_to_message.from_user.id
        user = await get_or_create_user(app.db, user_id)
        user["approved"] = True
        await app.db.users.replace_one({"_id": user_id}, user, upsert=True)
        await message.reply_text("User approved.")

    @app.on_message(filters.command("unapprove"))
    @catch_errors
    async def unapprove_handler(client, message: Message):
        if not await is_admin(message):
            return
        if not message.reply_to_message:
            await message.reply_text("Reply to a user to unapprove.")
            return
        user_id = message.reply_to_message.from_user.id
        user = await get_or_create_user(app.db, user_id)
        user["approved"] = False
        await app.db.users.replace_one({"_id": user_id}, user, upsert=True)
        await message.reply_text("User unapproved.")

    @app.on_message(filters.command("approved"))
    @catch_errors
    async def approved_list(client, message: Message):
        if not await is_admin(message):
            return
        users = app.db.users.find({"approved": True})
        names = []
        async for u in users:
            names.append(str(u["_id"]))
        await message.reply_text("Approved users:\n" + "\n".join(names))

    @app.on_message(filters.command("rmwarn"))
    @catch_errors
    async def rmwarn_handler(client, message: Message):
        if not await is_admin(message):
            return
        if not message.reply_to_message:
            await message.reply_text("Reply to user to remove warnings.")
            return
        user_id = message.reply_to_message.from_user.id
        user = await get_or_create_user(app.db, user_id)
        user["warnings"] = 0
        await app.db.users.replace_one({"_id": user_id}, user, upsert=True)
        await message.reply_text("Warnings cleared.")
