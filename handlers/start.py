from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from helpers.panels import main_panel
from config import Config


def register(app: Client):
    async def send_panel(message: Message):
        if Config.PANEL_IMAGE:
            await message.reply_photo(
                Config.PANEL_IMAGE,
                caption="**Control Panel**",
                reply_markup=main_panel(),
            )
        else:
            await message.reply(
                "**Control Panel**",
                reply_markup=main_panel(),
                parse_mode="markdown",
            )

    @app.on_message(filters.command(["start", "menu", "help"]))
    async def start(_, message: Message):
        await send_panel(message)

    @app.on_callback_query(filters.regex("^panel:"))
    async def handle_panel_buttons(client: Client, query: CallbackQuery):
        data = query.data

        if data == "panel:text_timer":
            await query.message.edit_text(
                "🗑 *Text Timer*\nSet how long text messages stay before deletion.\n\nUse:\n`/set_text_timer <seconds>`\nExample:\n`/set_text_timer 60`",
                reply_markup=main_panel(),
                parse_mode="markdown",
            )

        elif data == "panel:media_timer":
            await query.message.edit_text(
                "📷 *Media Timer*\nSet how long media files (photos/videos/docs) stay before deletion.\n\nUse:\n`/set_media_timer <seconds>`\nExample:\n`/set_media_timer 120`",
                reply_markup=main_panel(),
                parse_mode="markdown",
            )

        elif data == "panel:broadcast":
            await query.message.edit_text(
                "📢 *Broadcast Command*\nSend a message to all groups.\n\nUse:\n`/broadcast <your message>`\nExample:\n`/broadcast Hello everyone!`",
                reply_markup=main_panel(),
                parse_mode="markdown",
            )

        elif data == "panel:abuse_filter":
            await query.message.edit_text(
                "🛡 *Abuse Filter System*\nDelete abusive messages automatically.\n\nCommands:\n• `/addabuse <word>` — Block word\n• `/removeabuse <word>` — Unblock word",
                reply_markup=main_panel(),
                parse_mode="markdown",
            )

        await query.answer()
