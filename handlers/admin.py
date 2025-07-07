from pyrogram import filters
from pyrogram.types import Message

from utils import catch_errors, is_owner
from config import Config


def register(app):
    @app.on_message(filters.command("broadcast") & filters.user(Config.OWNER_ID))
    @catch_errors
    async def broadcast_handler(client, message: Message):
        if len(message.command) < 2:
            await message.reply_text("Usage: /broadcast <text>")
            return
        text = message.text.split(None, 1)[1]
        await message.reply_text(f"Broadcasting: {text}")
        # Placeholder for broadcast logic
