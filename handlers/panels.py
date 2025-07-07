from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import filters

from utils import perms, errors, db

PANEL = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
        [InlineKeyboardButton("📘 Help", callback_data="help")],
        [InlineKeyboardButton("👮 Admin", callback_data="admin")],
        [InlineKeyboardButton("🔄 Refresh", callback_data="refresh")],
    ]
)


def register(app):
    @app.on_message(filters.command(["start", "help", "menu"]))
    @errors.catch_errors
    async def show_panel(client, message: Message):
        if message.chat.type in ("group", "supergroup"):
            await db.add_group(app.db, message.chat.id)
        await message.reply_text("Control Panel", reply_markup=PANEL)
