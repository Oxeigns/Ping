from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from utils import catch_errors, safe_edit, get_or_create_user


def register(app):
    @app.on_message(filters.command("start"))
    @catch_errors
    async def start_handler(client, message: Message):
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Profile", callback_data="open_profile")]]
        )
        await message.reply_text(
            "Hello! I'm a moderation bot.", reply_markup=keyboard
        )

    @app.on_message(filters.command("help"))
    @catch_errors
    async def help_handler(client, message: Message):
        await message.reply_text("Help menu")

    @app.on_message(filters.command("ping"))
    @catch_errors
    async def ping_handler(client, message: Message):
        await message.reply_text("Pong!")

    @app.on_callback_query(filters.regex("^open_profile$"))
    async def cb_profile(client, callback):
        user = await get_or_create_user(app.db, callback.from_user.id)
        text = (
            f"**{callback.from_user.first_name}**\n"
            f"ID: `{callback.from_user.id}`\n"
            f"Toxicity: {user['global_toxicity_score']:.2f}\n"
            f"Warnings: {user['warnings']}"
        )
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Close", callback_data="close")]]
            ),
            disable_web_page_preview=True,
        )

    @app.on_callback_query(filters.regex("^close$"))
    async def close_cb(client, callback):
        await callback.message.delete()
