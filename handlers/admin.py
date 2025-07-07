from pyrogram import filters
from pyrogram.types import Message

from helpers import (
    catch_errors,
    is_owner,
    get_or_create_user,
    is_admin,
    approve_user,
)
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
        await approve_user(app.db, user_id, True)
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
        await approve_user(app.db, user_id, False)
        await message.reply_text("User unapproved.")

    @app.on_message(filters.command("approved"))
    @catch_errors
    async def approved_list(client, message: Message):
        if not await is_admin(message):
            return
        async with app.db.execute("SELECT id FROM users WHERE approved=1") as cur:
            rows = await cur.fetchall()
        names = [str(r[0]) for r in rows]
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
        await app.db.execute("UPDATE users SET warnings=0 WHERE id=?", (user_id,))
        await app.db.commit()
        await message.reply_text("Warnings cleared.")
