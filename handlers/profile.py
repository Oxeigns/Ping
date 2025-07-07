from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from utils import catch_errors, get_or_create_user


def build_profile_text(user, tg_user):
    text = [
        f"**{tg_user.first_name}**",
        f"ID: `{tg_user.id}`",
        f"Toxicity: {user['global_toxicity_score']:.2f}",
        f"Warnings: {user['warnings']}",
        f"Approved: {'Yes' if user.get('approved') else 'No'}",
    ]
    return "\n".join(text)


def register(app):
    @app.on_message(filters.command("profile"))
    @catch_errors
    async def profile_handler(client, message: Message):
        target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
        user = await get_or_create_user(app.db, target.id)
        text = build_profile_text(user, target)
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Close", callback_data="close")]]
        )
        await message.reply_text(text, reply_markup=keyboard, disable_web_page_preview=True)

    @app.on_callback_query(filters.regex("^close$"))
    async def close_cb(client, callback):
        await callback.message.delete()
