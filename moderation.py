import logging

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import ChatMemberUpdated, ChatPermissions, Message

from config import Config
from utils import (
    add_warning,
    catch_errors,
    check_image,
    check_toxicity,
    get_or_create_user,
)

logger = logging.getLogger(__name__)

TOXICITY_THRESHOLD = 0.85
NSFW_THRESHOLD = 0.85
WARN_THRESHOLD = 3


async def process_violation(client, message: Message, user_id: int, score: float, reason: str):
    try:
        await message.delete()
    except Exception:
        pass
    user = await add_warning(client.db, user_id, score)
    if user["warnings"] >= WARN_THRESHOLD:
        try:
            await message.chat.restrict(user_id, ChatPermissions())
            await client.send_message(
                message.chat.id,
                f"User {user_id} muted for repeated {reason} violations.",
            )
        except Exception:
            logger.exception("Failed to mute user")
    else:
        await client.send_message(
            message.chat.id,
            f"Warning for {reason}. Warnings: {user['warnings']}",
        )
    if Config.LOG_CHANNEL:
        await client.send_message(
            Config.LOG_CHANNEL,
            f"User {user_id} violated {reason} in chat {message.chat.id}",
        )


def register(app):
    @app.on_message(
        (
            filters.text
            | filters.photo
            | filters.sticker
            | filters.animation
            | filters.video
            | filters.document
        )
        & ~filters.service
    )
    @catch_errors
    async def moderate_messages(client, message: Message):
        if not message.from_user or message.from_user.is_self:
            return
        user = await get_or_create_user(app.db, message.from_user.id)
        if user.get("approved"):
            return

        if message.text:
            score = await check_toxicity(message.text)
            if score >= TOXICITY_THRESHOLD:
                await process_violation(client, message, message.from_user.id, score, "toxicity")
                return

        if message.photo or (
            message.document
            and message.document.mime_type
            and message.document.mime_type.startswith("image/")
        ) or (
            message.sticker and not (message.sticker.is_animated or message.sticker.is_video)
        ):
            target = (
                message.photo
                or message.document
                or message.sticker
            )
            file = await client.download_media(target.file_id, in_memory=True)
            result = await check_image(file)
            nudity = result.get("nudity", {}).get("sexual_activity", 0)
            drugs = result.get("drug", 0)
            value = max(nudity, drugs)
            if value >= NSFW_THRESHOLD:
                await process_violation(client, message, message.from_user.id, value, "nsfw")

    @app.on_chat_member_updated()
    async def check_new_member(client, chat_member: ChatMemberUpdated):
        if chat_member.new_chat_member.status not in {ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED}:
            return
        user = await get_or_create_user(app.db, chat_member.from_user.id)
        if user.get("approved"):
            return
        if user["warnings"] >= WARN_THRESHOLD:
            try:
                await client.restrict_chat_member(chat_member.chat.id, chat_member.from_user.id, ChatPermissions())
                await client.send_message(
                    chat_member.chat.id,
                    f"{chat_member.from_user.mention} muted due to previous violations.",
                )
            except Exception:
                logger.exception("Failed to restrict user on join")

