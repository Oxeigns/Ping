from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from helpers.panels import main_panel
from helpers import send_message_safe, safe_edit
from config import Config


def register(app: Client):
    async def send_panel(message: Message):
        if Config.PANEL_IMAGE:
            await message.reply_photo(
                Config.PANEL_IMAGE,
                caption="Control Panel",
                reply_markup=main_panel(),
            )
        else:
            await send_message_safe(message, "**Control Panel**", reply_markup=main_panel())

    @app.on_message(
        filters.command(["start", "menu", "help"]) & (filters.group | filters.private)
    )
    async def start(_, message: Message):
        await send_panel(message)

    @app.on_callback_query(filters.regex("^panel:"))
    async def handle_panel_buttons(client: Client, query: CallbackQuery):
        data = query.data

        if data == "panel:text_timer":
            await safe_edit(
                query.message,
                "🗑 *Text Timer*\nSet how long text messages stay before deletion.\n\nUse:\n`/set_text_timer <seconds>`\nExample:\n`/set_text_timer 60`",
                reply_markup=main_panel(),
            )

        elif data == "panel:media_timer":
            await safe_edit(
                query.message,
                "📷 *Media Timer*\nSet how long media files (photos/videos/docs) stay before deletion.\n\nUse:\n`/set_media_timer <seconds>`\nExample:\n`/set_media_timer 120`",
                reply_markup=main_panel(),
            )

        elif data == "panel:broadcast":
            await safe_edit(
                query.message,
                "📢 *Broadcast Command*\nSend a message to all groups.\n\nUse:\n`/broadcast <your message>`\nExample:\n`/broadcast Hello everyone!`",
                reply_markup=main_panel(),
            )

        elif data == "panel:abuse_filter":
            await safe_edit(
                query.message,
                "🛡 *Abuse Filter System*\n"
                "Delete abusive messages automatically across languages. "
                "Messages containing words from `banned_words.txt` are removed "
                "and the sender is warned. Group owners can whitelist words.\n\n"
                "Commands:\n"
                "• `/addabuse <word>` — Block word globally\n"
                "• `/removeabuse <word>` — Unblock word globally",
                reply_markup=main_panel(),
            )

        elif data == "panel:whitelist_word":
            await safe_edit(
                query.message,
                "⚪ *Whitelist System*\n\n"
                "• `/whitelist <word>` – Allow a banned word in this group\n"
                "• `/removewhitelist <word>` – Re-block that word\n"
                "🔒 Only group *owner* can use these commands.",
                reply_markup=main_panel(),
            )

        await query.answer()

    @app.on_message(filters.command("ping") & (filters.group | filters.private))
    async def ping(_, message: Message):
        await message.reply_text("pong")
