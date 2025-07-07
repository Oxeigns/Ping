from pyrogram import filters
from pyrogram.types import Message, ChatPermissions

from utils import update_violation, catch_errors

BANNED_WORDS = {"badword", "hate"}


def register(app):
    @app.on_message(filters.text & ~filters.private)
    @catch_errors
    async def text_moderation(client, message: Message):
        if not message.from_user or message.from_user.is_self:
            return
        text = message.text.lower()
        if any(word in text for word in BANNED_WORDS):
            user = await update_violation(app.db, message.from_user.id, 10, "warned")
            if user["violations"] >= 3:
                await message.chat.restrict(message.from_user.id, ChatPermissions())
                await message.reply_text("User muted for repeated violations.")
            else:
                await message.reply_text("Please keep the chat civil.")
