import logging
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from datetime import datetime
from telegram.error import BadRequest
from telegram.constants import ChatType, ChatMemberStatus, ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    ChatMemberHandler,
    filters,
)

from helpers import (
    get_or_create_user,
    upsert_group,
    remove_group,
    catch_errors,
)

logger = logging.getLogger(__name__)

def register(app: Application):
    def main_menu() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🛠️ Configure Group", callback_data="settings")],
                [InlineKeyboardButton("📢 Broadcast", callback_data="bc")],
                [InlineKeyboardButton("📘 Help", callback_data="help")],
                [InlineKeyboardButton("👨‍💻 Developer", callback_data="dev")],
            ]
        )

    COMMANDS = {
        "start", "menu", "help", "ping",
        "approve", "unapprove", "approved", "rmwarn", "broadcast",
    }

    @catch_errors
    async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.effective_message
        logger.info(
            "Command %s from %s in %s",
            message.text.split()[0].lower(),
            update.effective_user.id,
            update.effective_chat.id,
        )

        if message.chat.type == ChatType.PRIVATE:
            await get_or_create_user(app.db, update.effective_user.id)
            if app.config.LOG_CHANNEL:
                try:
                    await context.bot.send_message(
                        app.config.LOG_CHANNEL,
                        f"🔔 <b>Start</b> - {update.effective_user.mention_html()} (@{update.effective_user.username or 'n/a'})",
                        parse_mode=ParseMode.HTML,
                    )
                except Exception as e:
                    logger.debug("failed to log start: %s", e)

        name = update.effective_user.first_name
        caption = (
            f"**👋 Welcome {name}!**\n\n"
            "Use the control panel below to manage your profile, broadcast, or get help."
        )

        image = getattr(app.config, "PANEL_IMAGE", None)
        if image:
            try:
                await message.reply_photo(
                    image,
                    caption=caption,
                    reply_markup=main_menu(),
                )
                return
            except Exception as e:
                logger.debug("failed to send panel image: %s", e)

        await message.reply_text(
            caption,
            reply_markup=main_menu(),
            disable_web_page_preview=True,
        )

    @catch_errors
    async def ping_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info("/ping by %s in %s", update.effective_user.id, update.effective_chat.id)
        delta = datetime.utcnow() - context.application.start_time
        seconds = int(delta.total_seconds())
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        uptime = f"{hours}h{minutes}m{secs}s"
        await update.effective_message.reply_text(f"🏓 Pong! Uptime: {uptime}")

    def _help_text() -> str:
        return (
            "**📘 Bot Help**\n\n"
            "• `/approve` - Approve user\n"
            "• `/unapprove` - Revoke approval\n"
            "• `/broadcast` - Owner broadcast\n"
            "• `/rmwarn` - Reset warnings\n"
            "• `/start`, `/menu`, `/help` - Show control panel"
        )

    @catch_errors
    async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.effective_message.reply_text(_help_text(), disable_web_page_preview=True)


    @catch_errors
    async def cb_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        help_text = _help_text()
        try:
            await query.message.edit_text(
                help_text,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_home")]]
                ),
                disable_web_page_preview=True,
            )
        except BadRequest as e:
            if "Message is not modified" not in str(e):
                raise

    @catch_errors
    async def cb_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        await query.message.edit_text(
            "**🛠 Group Configuration**\n\nComing soon...",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_home")]]
            ),
            disable_web_page_preview=True,
        )

    @catch_errors
    async def cb_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        await query.message.edit_text(
            "Use /broadcast <msg>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_home")]]
            ),
            disable_web_page_preview=True,
        )

    @catch_errors
    async def cb_dev(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer(
            text=f"👨‍💻 Developer: {app.config.DEV_NAME}\nContact: {app.config.DEV_URL}",
            show_alert=True,
        )

    @catch_errors
    async def cb_back_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        text = "**👋 Welcome back to the main menu!**"
        try:
            await query.message.edit_text(
                text,
                reply_markup=main_menu(),
                disable_web_page_preview=True,
            )
        except BadRequest:
            await query.message.edit_caption(
                text,
                reply_markup=main_menu(),
                disable_web_page_preview=True,
            )

    @catch_errors
    async def track_my_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
        member = update.my_chat_member
        chat = member.chat
        old = member.old_chat_member.status
        new = member.new_chat_member.status
        actor = member.from_user

        if new in {ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR} and old in {ChatMemberStatus.LEFT, ChatMemberStatus.KICKED}:
            try:
                members = await context.bot.get_chat_member_count(chat.id)
            except Exception:
                members = 0
            link = f"https://t.me/{chat.username}" if chat.username else ""
            await upsert_group(app.db, chat.id, chat.title or "", chat.username, members, link)
            text = (
                f"✅ Added to <b>{chat.title}</b>\n"
                f"Members: {members}\n"
                f"Link: {link or 'N/A'}\n"
                f"By: {actor.mention_html()}"
            )
        elif new in {ChatMemberStatus.LEFT, ChatMemberStatus.KICKED}:
            await remove_group(app.db, chat.id)
            text = (
                f"❌ Removed from <b>{chat.title}</b>\n"
                f"By: {actor.mention_html()}"
            )
        else:
            return
        if app.config.LOG_CHANNEL:
            try:
                await context.bot.send_message(app.config.LOG_CHANNEL, text, parse_mode=ParseMode.HTML)
            except Exception as e:
                logger.debug("failed to log group event: %s", e)

    @catch_errors
    async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
        command = update.message.text.split()[0][1:].split("@")[0].lower()
        if command not in COMMANDS:
            await update.message.reply_text("❌ Unknown command. Use /help to see available options.")

    app.add_handler(CommandHandler(["start", "menu"], start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("ping", ping_handler))
    app.add_handler(CallbackQueryHandler(cb_help, pattern="^help$"))
    app.add_handler(CallbackQueryHandler(cb_settings, pattern="^settings$"))
    app.add_handler(CallbackQueryHandler(cb_broadcast, pattern="^bc$"))
    app.add_handler(CallbackQueryHandler(cb_dev, pattern="^dev$"))
    app.add_handler(CallbackQueryHandler(cb_back_home, pattern="^back_home$"))
    app.add_handler(ChatMemberHandler(track_my_member, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.COMMAND, unknown), group=999)

    logger.info("✅ Start handlers registered.")
