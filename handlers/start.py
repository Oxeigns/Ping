import logging
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from helpers import get_or_create_user

logger = logging.getLogger(__name__)

def register(app: Application):
    def main_menu() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("📊 View My Profile", callback_data="open_profile")],
                [InlineKeyboardButton("🛠️ Configure Group", callback_data="settings")],
                [InlineKeyboardButton("📢 Broadcast", callback_data="bc")],
                [InlineKeyboardButton("📘 Help", callback_data="help")],
                [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/Oxeign")],
            ]
        )

    COMMANDS = {
        "start", "menu", "help", "ping", "profile",
        "approve", "unapprove", "approved", "rmwarn", "broadcast",
    }

    async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.effective_message
        logger.info(
            "Command %s from %s in %s",
            message.text.split()[0].lower(),
            update.effective_user.id,
            update.effective_chat.id,
        )
        await message.reply_text(
            "**👋 Welcome to the Advanced Moderation Bot!**\n\n"
            "Use the control panel below to manage your profile, broadcast, or get help.",
            reply_markup=main_menu(),
            disable_web_page_preview=True,
        )

    async def ping_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info("/ping by %s in %s", update.effective_user.id, update.effective_chat.id)
        await update.effective_message.reply_text("🏓 Pong!")

    async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.effective_message
        logger.info("/profile by %s in %s", update.effective_user.id, update.effective_chat.id)
        target = message.reply_to_message.from_user if message.reply_to_message else update.effective_user
        tg_user = await context.bot.get_chat(target.id)
        user = await get_or_create_user(app.db, tg_user.id)

        text = (
            f"**👤 {tg_user.first_name}**\n"
            f"🆔 ID: `{tg_user.id}`\n"
            f"💢 Toxicity: `{user['global_toxicity']:.2f}`\n"
            f"⚠️ Warnings: `{user['warnings']}`\n"
            f"✅ Approved: {'Yes' if user.get('approved') else 'No'}"
        )

        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Close", callback_data="close")]])
        try:
            photos = await context.bot.get_user_profile_photos(tg_user.id, limit=1)
            if photos.total_count:
                file = await photos.photos[0][-1].get_file()
                photo = await file.download_as_bytearray()
                await message.reply_photo(photo, caption=text, reply_markup=keyboard)
                return
        except Exception as e:
            logger.debug("failed to send photo: %s", e)

        await message.reply_text(text, reply_markup=keyboard, disable_web_page_preview=True)

    async def cb_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        tg_user = await context.bot.get_chat(query.from_user.id)
        user = await get_or_create_user(app.db, tg_user.id)
        text = (
            f"**👤 {tg_user.first_name}**\n"
            f"🆔 ID: `{tg_user.id}`\n"
            f"💢 Toxicity: `{user['global_toxicity']:.2f}`\n"
            f"⚠️ Warnings: `{user['warnings']}`\n"
            f"✅ Approved: {'Yes' if user.get('approved') else 'No'}"
        )
        try:
            photos = await context.bot.get_user_profile_photos(tg_user.id, limit=1)
            if photos.total_count:
                await query.message.edit_media(
                    InputMediaPhoto(photos.photos[0][-1].file_id, caption=text),
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_home")]]
                    ),
                )
                return
        except Exception as e:
            logger.debug("failed to edit media: %s", e)

        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_home")]]
            ),
            disable_web_page_preview=True,
        )

    async def cb_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        await query.message.edit_text(
            "**📘 Bot Help**\n\n"
            "`/profile` - View your moderation profile\n"
            "`/approve` - Approve user\n"
            "`/unapprove` - Revoke approval\n"
            "`/broadcast` - Owner broadcast\n"
            "`/rmwarn` - Reset warnings\n"
            "`/start`, `/menu`, `/help` - Show control panel",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_home")]]
            ),
            disable_web_page_preview=True,
        )

    async def cb_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer("🛠️ Group settings panel will be available soon!", show_alert=True)

    async def cb_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        await query.message.edit_text(
            "📢 Only the bot owner can use:\n\n`/broadcast <message>`",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_home")]]
            ),
            disable_web_page_preview=True,
        )

    async def cb_back_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        await query.message.edit_text(
            "**👋 Welcome back to the main menu!**",
            reply_markup=main_menu(),
            disable_web_page_preview=True,
        )

    async def close_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        await query.message.delete()

    async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
        command = update.message.text.split()[0][1:].split("@")[0].lower()
        if command not in COMMANDS:
            await update.message.reply_text("❌ Unknown command. Use /help to see available options.")

    app.add_handler(CommandHandler(["start", "menu", "help"], start_handler))
    app.add_handler(CommandHandler("ping", ping_handler))
    app.add_handler(CommandHandler("profile", profile_handler))
    app.add_handler(CallbackQueryHandler(cb_profile, pattern="^open_profile$"))
    app.add_handler(CallbackQueryHandler(cb_help, pattern="^help$"))
    app.add_handler(CallbackQueryHandler(cb_settings, pattern="^settings$"))
    app.add_handler(CallbackQueryHandler(cb_broadcast, pattern="^bc$"))
    app.add_handler(CallbackQueryHandler(cb_back_home, pattern="^back_home$"))
    app.add_handler(CallbackQueryHandler(close_cb, pattern="^close$"))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.COMMAND, unknown), group=999)

    logger.info("✅ Start handlers registered.")
