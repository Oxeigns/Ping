from pyrogram import filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from helpers import catch_errors, get_or_create_user


def register(app):
    def main_menu():
        return InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("\ud83d\udcca View My Profile", callback_data="open_profile")],
                [InlineKeyboardButton("\ud83d\udd27 Configure Group", callback_data="settings")],
                [InlineKeyboardButton("\ud83d\udce2 Broadcast", callback_data="bc")],
                [InlineKeyboardButton("\ud83d\udcdc Help", callback_data="help")],
                [InlineKeyboardButton("\ud83d\udc68\u200d\ud83d\udcbb Developer", url="https://t.me/{0}".format("Oxeign"))],
            ]
        )

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

    @app.on_message(filters.command(["start", "menu", "help"]) & filters.private)
    @catch_errors
    async def start_handler(client, message: Message):
        await message.reply_text(
            "**Welcome to the Moderation Bot**",
            reply_markup=main_menu(),
            disable_web_page_preview=True,
        )

    @app.on_message(filters.command("ping") & filters.private)
    @catch_errors
    async def ping_handler(client, message: Message):
        await message.reply_text("Pong!")

    @app.on_callback_query(filters.regex("^open_profile$"))
    async def cb_profile(client, callback: CallbackQuery):
        await callback.answer()
        user = await get_or_create_user(app.db, callback.from_user.id)
        text = (
            f"**{callback.from_user.first_name}**\n"
            f"ID: `{callback.from_user.id}`\n"
            f"Toxicity: {user['global_toxicity']:.2f}\n"
            f"Warnings: {user['warnings']}"
        )
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Close", callback_data="close")]]
            ),
            disable_web_page_preview=True,
        )

    @app.on_callback_query(filters.regex("^help$"))
    async def cb_help(client, callback: CallbackQuery):
        await callback.answer()
        await callback.message.edit_text(
            "Use /help to see available commands.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="close")]]),
        )

    @app.on_callback_query(filters.regex("^settings$"))
    async def cb_settings(client, callback: CallbackQuery):
        await callback.answer("Settings feature coming soon", show_alert=True)

    @app.on_callback_query(filters.regex("^bc$"))
    async def cb_broadcast(client, callback: CallbackQuery):
        await callback.answer()
        await callback.message.edit_text(
            "Only the owner can use /broadcast <text>.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="close")]]),
        )

    @app.on_callback_query(filters.regex("^close$"))
    async def close_cb(client, callback: CallbackQuery):
        await callback.answer()
        await callback.message.delete()

    @app.on_message(filters.regex("^/") & filters.private, group=1)
    async def unknown(client, message: Message):
        command = message.text.split()[0][1:].split("@")[0].lower()
        if command in COMMANDS:
            return
        await message.reply_text("Unknown command. Use /help.")
