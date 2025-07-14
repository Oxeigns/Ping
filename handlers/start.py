from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
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

    @app.on_callback_query()
    async def panel_callbacks(_, query: CallbackQuery):
        data = query.data
        if data == "text_timer":
            await query.message.edit_text(
                "🗑 **Text Timer Setup**\n"
                "Set how long text messages stay before deletion.\n\n"
                "Usage:\n`/set_text_timer <seconds>`",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("◀️ Back", callback_data="main_panel")]]
                ),
                parse_mode="markdown",
            )
        elif data == "media_timer":
            await query.message.edit_text(
                "📷 **Media Timer Setup**\n"
                "Control when photos and other media are removed.\n\n"
                "Usage:\n`/set_media_timer <seconds>`",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("◀️ Back", callback_data="main_panel")]]
                ),
                parse_mode="markdown",
            )
        elif data == "broadcast_panel":
            await query.message.edit_text(
                "📢 **Broadcast Messages**\n"
                "Send a message to all added chats.\n\n"
                "Usage:\n`/broadcast <message>`",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("◀️ Back", callback_data="main_panel")]]
                ),
                parse_mode="markdown",
            )
        elif data == "abuse_panel":
            await query.message.edit_text(
                "🛡 **Abuse Filter**\n"
                "Manage abusive words that trigger deletion.\n\n"
                "Add word: `/addabuse <word>`\n"
                "Remove word: `/removeabuse <word>`",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("◀️ Back", callback_data="main_panel")]]
                ),
                parse_mode="markdown",
            )
        elif data == "main_panel":
            await query.message.edit_text(
                "**Control Panel**",
                reply_markup=main_panel(),
                parse_mode="markdown",
            )
        else:
            await query.answer()
