import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
from helpers.mongo import get_db
from helpers.decorators import catch_errors

logger = logging.getLogger(__name__)


def register(app: Client):
    db = get_db()

    @app.on_message(filters.new_chat_members & filters.group)
    @catch_errors
    async def track_bot_added(client: Client, message: Message):
        me = await client.get_me()
        if any(m.id == me.id for m in message.new_chat_members):
            await db.group_settings.update_one(
                {"chat_id": message.chat.id},
                {"$setOnInsert": {"chat_id": message.chat.id}},
                upsert=True,
            )
            logger.info("[GENERAL] Bot added to group %s", message.chat.id)
            if Config.LOG_CHANNEL:
                try:
                    text = f"➕ Bot added to group {message.chat.id}"
                    await client.send_message(Config.LOG_CHANNEL, text)
                except Exception as exc:
                    logger.warning("Failed to send log: %s", exc)

    @app.on_message(filters.left_chat_member & filters.group)
    @catch_errors
    async def track_bot_left(client: Client, message: Message):
        me = await client.get_me()
        if message.left_chat_member and message.left_chat_member.id == me.id:
            await db.group_settings.delete_one({"chat_id": message.chat.id})
            logger.info("[GENERAL] Bot removed from group %s", message.chat.id)
            if Config.LOG_CHANNEL:
                try:
                    text = f"➖ Bot removed from group {message.chat.id}"
                    await client.send_message(Config.LOG_CHANNEL, text)
                except Exception as exc:
                    logger.warning("Failed to send log: %s", exc)
