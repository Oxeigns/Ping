from pyrogram import filters
from pyrogram.types import Message

from utils import db, errors


def register(app):
    @app.on_message(filters.command("ping"))
    @errors.catch_errors
    async def ping(client, message: Message):
        await message.reply_text("Pong!")

    @app.on_message(filters.command("profile") & filters.private)
    @errors.catch_errors
    async def profile(client, message: Message):
        user = await db.get_user(app.db, message.from_user.id)
        text = (
            f"👤 {message.from_user.mention}\n"
            f"🧪 Toxicity Score: {user.get('score', 0)}\n"
            f"Warnings: {user.get('warnings', {}).get(str(message.chat.id), 0)}"
        )
        await message.reply_text(text)
