from pyrogram import filters
from pyrogram.types import Message

from utils import catch_errors, safe_edit


def register(app):
    @app.on_message(filters.command("start"))
    @catch_errors
    async def start_handler(client, message: Message):
        await message.reply_text("Hello! I'm a moderation bot.")

    @app.on_message(filters.command("help"))
    @catch_errors
    async def help_handler(client, message: Message):
        await message.reply_text("Help menu")

    @app.on_message(filters.command("ping"))
    @catch_errors
    async def ping_handler(client, message: Message):
        await message.reply_text("Pong!")
