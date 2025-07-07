from pyrogram import filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    InputMediaPhoto,
)

from helpers import catch_errors, get_or_create_user


def register(app):
    def main_menu():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 View My Profile", callback_data="open_profile")],
            [InlineKeyboardButton("🛠️ Configure Group", callback_data="settings")],
            [InlineKeyboardButton("📢 Broadcast", callback_data="bc")],
            [InlineKeyboardButton("📘 Help", callback_data="help")],
            [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/Oxeign")],
        ])

    COMMANDS = {
        "start",
        "menu",
        "help",
        "ping",
        "profile",
        "approve",
        "unapprove",
        "approved",
        "rmwarn",
        "broadcast",
    }

    @app.on_message(filters.command(["start", "menu", "help"]))
    @catch_errors
    async def start_handler(client, message: Message):
        await message.reply_text(
            "**👋 Welcome to the Advanced Moderation Bot!**\n\n"
            "Use the control panel below to manage your profile, broadcast, or get help.",
            reply_markup=main_menu(),
            disable_web_page_preview=True,
        )

    @app.on_message(filters.command("ping"))
    @catch_errors
    async def ping_handler(client, message: Message):
        await message.reply_text("🏓 Pong!")

    @app.on_callback_query(filters.regex("^open_profile$"))
    async def cb_profile(client, callback: CallbackQuery):
        await callback.answer()
        tg_user = await client.get_users(callback.from_user.id)
        user = await get_or_create_user(app.db, tg_user.id)
        text = (
            f"**👤 {tg_user.first_name}**\n"
            f"🆔 ID: `{tg_user.id}`\n"
            f"💢 Toxicity: `{user['global_toxicity']:.2f}`\n"
            f"⚠️ Warnings: `{user['warnings']}`\n"
            f"✅ Approved: {'Yes' if user.get('approved') else 'No'}"
        )
        photo_id = tg_user.photo.big_file_id if tg_user.photo else None
        if photo_id:
            try:
                await callback.message.edit_media(
                    InputMediaPhoto(photo_id, caption=text),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_home")],
                    ]),
                )
                return
            except Exception:
                pass

        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_home")],
            ]),
            disable_web_page_preview=True,
        )

    @app.on_callback_query(filters.regex("^help$"))
    async def cb_help(client, callback: CallbackQuery):
        await callback.answer()
        await callback.message.edit_text(
            "**📘 Bot Help**\n\n"
            "`/profile` - View your moderation profile\n"
            "`/approve` - Approve user\n"
            "`/unapprove` - Revoke approval\n"
            "`/broadcast` - Owner broadcast\n"
            "`/rmwarn` - Reset warnings\n"
            "`/start`, `/menu`, `/help` - Show control panel",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_home")],
            ]),
            disable_web_page_preview=True,
        )

    @app.on_callback_query(filters.regex("^settings$"))
    async def cb_settings(client, callback: CallbackQuery):
        await callback.answer("🛠️ Group settings panel will be available soon!", show_alert=True)

    @app.on_callback_query(filters.regex("^bc$"))
    async def cb_broadcast(client, callback: CallbackQuery):
        await callback.answer()
        await callback.message.edit_text(
            "📢 Only the bot owner can use:\n\n`/broadcast <message>`",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_home")],
            ]),
            disable_web_page_preview=True,
        )

    @app.on_callback_query(filters.regex("^back_home$"))
    async def cb_back_home(client, callback: CallbackQuery):
        await callback.answer()
        await callback.message.edit_text(
            "**👋 Welcome back to the main menu!**",
            reply_markup=main_menu(),
            disable_web_page_preview=True,
        )

    @app.on_callback_query(filters.regex("^close$"))
    async def close_cb(client, callback: CallbackQuery):
        await callback.answer()
        await callback.message.delete()

    @app.on_message(filters.regex("^/") & filters.private, group=1)
    async def unknown(client, message: Message):
        command = message.text.split()[0][1:].split("@")[0].lower()
        if command not in COMMANDS:
            await message.reply_text("❌ Unknown command. Use /help to see available options.")
