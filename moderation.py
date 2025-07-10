import logging
from telegram import Update, ChatPermissions
from telegram.constants import ChatMemberStatus, ParseMode
from telegram.ext import (
    Application,
    MessageHandler,
    ChatMemberHandler,
    ContextTypes,
    filters,
)

from config import Config
from helpers import (
    add_warning,
    add_log,
    check_image,
    check_toxicity,
    get_or_create_user,
    is_admin,
)

logger = logging.getLogger(__name__)

TOXICITY_THRESHOLD = 0.85
NSFW_THRESHOLD = 0.85
WARN_THRESHOLD = 3

SAFE_COMMANDS = [
    "start", "menu", "help", "ping", "profile",
    "approve", "unapprove", "broadcast"
]

async def process_violation(application: Application, message, user_id: int, score: float, reason: str):
    logger.warning("🔴 Violation Detected | Reason: %s | Score: %.2f | User: %d", reason, score, user_id)

    try:
        await message.delete()
    except Exception as e:
        logger.error("Failed to delete message: %s", e)

    user = await add_warning(application.db, user_id, score)
    await add_log(application.db, user_id, message.chat.id, reason, score)

    if user["warnings"] >= WARN_THRESHOLD:
        try:
            await application.bot.restrict_chat_member(message.chat.id, user_id, ChatPermissions())
            await application.bot.send_message(
                message.chat.id,
                f"🔇 <b>User {user_id} has been muted for repeated {reason} violations.</b>",
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            logger.exception("Failed to mute user")
    else:
        await application.bot.send_message(
            message.chat.id,
            f"⚠️ <b>Warning issued for {reason}</b>\nTotal warnings: <code>{user['warnings']}</code>",
            parse_mode=ParseMode.HTML,
        )

    if Config.LOG_CHANNEL:
        try:
            await application.bot.send_message(
                Config.LOG_CHANNEL,
                f"📛 Violation Log:\n<b>User:</b> <code>{user_id}</code>\n<b>Chat:</b> <code>{message.chat.id}</code>\n<b>Reason:</b> {reason}\n<b>Score:</b> {score}",
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            logger.warning("Could not send log to LOG_CHANNEL")

def register(app: Application):
    # Ignore commands and service messages in moderation
    async def moderate_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.effective_message
        if not message or not update.effective_user:
            return

        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

        if user_id == Config.OWNER_ID or await is_admin(message):
            return

        user = await get_or_create_user(app.db, user_id)
        if user.get("approved"):
            return

        text = message.text or message.caption
        if text:
            score = await check_toxicity(text)
            if score >= TOXICITY_THRESHOLD:
                await process_violation(context.application, message, user_id, score, "toxicity")
                return

        media = None
        if message.photo:
            media = message.photo.file_id
        elif message.video:
            media = message.video.file_id
        elif message.animation:
            media = message.animation.file_id
        elif message.sticker:
            media = message.sticker.file_id
        elif message.document and message.document.mime_type.startswith("image/"):
            media = message.document.file_id

        if media:
            file = await context.bot.get_file(media)
            file = await file.download_as_bytearray()
            result = await check_image(file)
            nudity = result.get("nudity", {}).get("sexual_activity", 0)
            drugs = result.get("drug", 0)
            score = max(nudity, drugs)
            if score >= NSFW_THRESHOLD:
                await process_violation(context.application, message, user_id, score, "nsfw")

    async def check_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_member = update.chat_member
        if chat_member.new_chat_member.status not in {
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.RESTRICTED,
        }:
            return

        user_id = chat_member.from_user.id
        chat_id = chat_member.chat.id

        user = await get_or_create_user(app.db, user_id)
        if user.get("approved"):
            return

        if user["warnings"] >= WARN_THRESHOLD:
            try:
                await context.bot.restrict_chat_member(chat_id, user_id, ChatPermissions())
                await context.bot.send_message(
                    chat_id,
                    f"🔇 <b>{chat_member.from_user.mention} was muted on join due to past violations.</b>",
                    parse_mode=ParseMode.HTML,
                )
            except Exception:
                logger.exception("Failed to restrict user on join")

    app.add_handler(MessageHandler(~filters.StatusUpdate.ALL, moderate_messages))
    app.add_handler(ChatMemberHandler(check_new_member, ChatMemberHandler.CHAT_MEMBER))

    logger.info("✅ Moderation handlers registered successfully.")
