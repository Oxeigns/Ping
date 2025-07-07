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
        await message.reply_text("Broadcasting...")
        sent = 0
        async for dialog in app.get_dialogs():
            if dialog.chat.type in ("group", "supergroup"):
                try:
                    await app.send_message(dialog.chat.id, text)
                    sent += 1
                except Exception:
                    continue
        await message.reply_text(f"Broadcast sent to {sent} chats.")
