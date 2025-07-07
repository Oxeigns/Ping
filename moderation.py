import logging
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus, ParseMode
from pyrogram.types import Message, ChatMemberUpdated, ChatPermissions

from config import Config
from helpers import (
    add_warning,
    add_log,
    catch_errors,
    check_image,
    check_toxicity,
    get_or_create_user,
    is_admin,
)

logger = logging.getLogger(__name__)

TOXICITY_THRESHOLD = 0.85
NSFW_THRESHOLD = 0.85
WARN_THRESHOLD = 3


async def process_violation(client, message: Message, user_id: int, score: float, reason: str):
    logger.warning("🔴 Violation Detected | Reason: %s | Score: %.2f | User: %d", reason, score, user_id)

    try:
        await message.delete()
    except Exception as e:
        logger.error("Failed to delete message: %s", e)

    user = await add_warning(client.db, user_id, score)
    await add_log(client.db, user_id, message.chat.id, reason, score)

    if user["warnings"] >= WARN_THRESHOLD:
        try:
            await message.chat.restrict(user_id, ChatPermissions())
            await client.send_message(
                message.chat.id,
                f"🔇 <b>User {user_id} has been muted for repeated {reason} violations.</b>",
                parse_mode=ParseMode.HTML
            )
        except Exception:
            logger.exception("Failed to mute user")
    else:
        await client.send_message(
            message.chat.id,
            f"⚠️ <b>Warning issued for {reason}</b>\nTotal warnings: <code>{user['warnings']}</code>",
            parse_mode=ParseMode.HTML
        )

    if Config.LOG_CHANNEL:
        try:
            await client.send_message(
                Config.LOG_CHANNEL,
                f"📛 Violation Log:\n<b>User:</b> <code>{user_id}</code>\n<b>Chat:</b> <code>{message.chat.id}</code>\n<b>Reason:</b> {reason}\n<b>Score:</b> {score}",
                parse_mode=ParseMode.HTML
            )
        except Exception:
            logger.warning("Could not send log to LOG_CHANNEL")


def register(app):
    @app.on_message(~filters.service, group=1)
    @catch_errors
    async def moderate_messages(client, message: Message):
        if not message.from_user or message.from_user.is_self:
            return

        user_id = message.from_user.id
        chat_id = message.chat.id

        if user_id == Config.OWNER_ID or await is_admin(message):
            return

        user = await get_or_create_user(app.db, user_id)
        if user.get("approved"):
            return

        text = message.text or message.caption
        if text:
            score = await check_toxicity(text)
            if score >= TOXICITY_THRESHOLD:
                await process_violation(client, message, user_id, score, "toxicity")
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
            file = await client.download_media(media, in_memory=True)
            result = await check_image(file)
            nudity = result.get("nudity", {}).get("sexual_activity", 0)
            drugs = result.get("drug", 0)
            score = max(nudity, drugs)
            if score >= NSFW_THRESHOLD:
                await process_violation(client, message, user_id, score, "nsfw")

    @app.on_chat_member_updated()
    async def check_new_member(client, chat_member: ChatMemberUpdated):
        if chat_member.new_chat_member.status not in {
            ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED
        }:
            return

        user_id = chat_member.from_user.id
        chat_id = chat_member.chat.id

        user = await get_or_create_user(app.db, user_id)
        if user.get("approved"):
            return

        if user["warnings"] >= WARN_THRESHOLD:
            try:
                await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
                await client.send_message(
                    chat_id,
                    f"🔇 <b>{chat_member.from_user.mention} was muted on join due to past violations.</b>",
                    parse_mode=ParseMode.HTML
                )
            except Exception:
                logger.exception("Failed to restrict user on join")

    logger.info("✅ Moderation handlers registered successfully.")
