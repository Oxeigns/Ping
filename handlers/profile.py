from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatType

from helpers import catch_errors, get_or_create_user


def build_profile_text(user, tg_user):
    text = [
        f"👤 **{tg_user.first_name}**",
        f"🆔 ID: `{tg_user.id}`",
        f"💢 Toxicity Score: `{user['global_toxicity']:.2f}`",
        f"⚠️ Warnings: `{user['warnings']}`",
        f"✅ Approved: {'Yes' if user.get('approved') else 'No'}",
    ]
    return "\n".join(text)


def register(app):
    @app.on_message(filters.command("profile") & filters.private)
    @catch_errors
    async def profile_handler(client, message: Message):
        target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
        user = await get_or_create_user(app.db, target.id)
        text = build_profile_text(user, target)
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("❌ Close", callback_data="close")]]
        )
        try:
            if target.photo:
                photo = await client.download_media(target.photo.big_file_id, in_memory=True)
                await message.reply_photo(photo, caption=text, reply_markup=keyboard)
                return
        except Exception:
            pass

        await message.reply_text(text, reply_markup=keyboard, disable_web_page_preview=True)

    @app.on_callback_query(filters.regex("^close$"))
    async def close_cb(client, callback):
        await callback.answer()
        await callback.message.delete()
