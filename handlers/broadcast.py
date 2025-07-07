from pyrogram import filters
from pyrogram.types import Message

from config import Config
from utils import db, errors, logger


def register(app):
    @app.on_message(filters.command("broadcast") & filters.user(Config.OWNER_ID))
    @errors.catch_errors
    async def broadcast_handler(client, message: Message):
        if len(message.command) < 2:
            await message.reply_text("Usage: /broadcast <text>")
            return
        text = message.text.split(None, 1)[1]
        groups = await db.get_groups(app.db)
        for chat_id in groups:
            try:
                await client.send_message(chat_id, text)
            except Exception:
                pass
        await message.reply_text("Broadcast sent")
        await logger.log_action(app, "Broadcast executed")
