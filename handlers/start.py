from pyrogram import Client, filters
from pyrogram.types import Message
from helpers.panels import main_panel


def register(app: Client):
    @app.on_message(filters.command("start") & filters.private)
    async def start(_, message: Message):
        await message.reply("Hello!", reply_markup=main_panel())
