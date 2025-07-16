from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from config import Config
from helpers import send_message_safe, safe_edit
from helpers.panels import (
    main_panel,
    moderation_panel,
    settings_panel,
    admin_panel,
    help_panel,
)


async def send_welcome(message: Message, bot_name: str) -> None:
    first = message.from_user.first_name if message.from_user else "there"
    text = f"👋 Hello {first}! I’m {bot_name}, your AI-powered group assistant."
    if Config.PANEL_IMAGE:
        await message.reply_photo(Config.PANEL_IMAGE, caption=text, reply_markup=main_panel())
    else:
        await send_message_safe(message, text, reply_markup=main_panel())


def register(app: Client):
    @app.on_message(filters.command(["start", "menu", "help"]) & (filters.group | filters.private))
    async def start_handler(client: Client, message: Message):
        me = await client.get_me()
        await send_welcome(message, me.first_name)
        if message.chat.type == "private" and Config.LOG_CHANNEL:
            user = message.from_user
            if user:
                log = (
                    f"#START\nID: {user.id}\nName: {user.first_name}"\
                    f"\nUser: @{user.username or 'N/A'}\nTime: {datetime.utcnow().isoformat()}"
                )
                try:
                    await client.send_message(Config.LOG_CHANNEL, log)
                except Exception:
                    pass

    @app.on_callback_query(filters.regex("^panel:"))
    async def callbacks(client: Client, query: CallbackQuery):
        data = query.data
        if data == "panel:mod":
            await safe_edit(query.message, "**Moderation**", reply_markup=moderation_panel())
        elif data == "panel:settings":
            await safe_edit(query.message, "**Settings**", reply_markup=settings_panel())
        elif data == "panel:admin":
            await safe_edit(query.message, "**Admin Tools**", reply_markup=admin_panel())
        elif data == "panel:status":
            await client.send_message(query.message.chat.id, "/status")
        elif data == "panel:help":
            await safe_edit(query.message, "**Help**", reply_markup=help_panel())
        elif data == "panel:text":
            await client.send_message(query.message.chat.id, "/off_text_delete")
        elif data == "panel:media":
            await client.send_message(query.message.chat.id, "/off_media_delete")
        elif data in {"panel:main", "panel:exit"}:
            me = await client.get_me()
            await safe_edit(query.message, f"👋 Hello {query.from_user.first_name}! I’m {me.first_name}, your AI-powered group assistant.", reply_markup=main_panel())
        await query.answer()

