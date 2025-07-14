from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
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

    @app.on_callback_query(filters.regex("^dev$"))
    async def dev_info(_, query: CallbackQuery):
        await query.answer(f"{Config.DEV_NAME}\n{Config.DEV_URL}", show_alert=True)

    @app.on_callback_query(filters.regex("^support$"))
    async def support_info(_, query: CallbackQuery):
        await query.answer(
            "Support:\n📢 https://t.me/botsyard\n💬 https://t.me/+Sn1PMhrr_nIwM2Y1",
            show_alert=True,
        )
