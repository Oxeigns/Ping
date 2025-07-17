import logging
from helpers.compat import Client, Message, filters
from config import Config
from helpers.mongo import get_db
from helpers.decorators import catch_errors
from .panels import send_welcome  # Correct import for welcome panel

logger = logging.getLogger(__name__)


def register(app: Client):
    db = get_db()

    @app.on_message(filters.new_chat_members & filters.group)
    @catch_errors
    async def track_bot_added(client: Client, message: Message):
        me = await client.get_me()
        new_members = message.new_chat_members

        # Check if bot was added
        if any(member.id == me.id for member in new_members):
            chat_id = message.chat.id

            # Save group to DB if new
            await db.group_settings.update_one(
                {"chat_id": chat_id},
                {"$setOnInsert": {"chat_id": chat_id}},
                upsert=True
            )

            logger.info("🤖 Bot added to group %s", chat_id)

            # Log to log channel
            if Config.LOG_CHANNEL:
                try:
                    await client.send_message(
                        Config.LOG_CHANNEL,
                        f"➕ Bot added to group `{chat_id}`",
                        parse_mode="Markdown"
                    )
                except Exception as exc:
                    logger.warning("LOG_CHANNEL error: %s", exc)

            # Send welcome panel
            try:
                await send_welcome(message, me.first_name)
            except Exception as exc:
                logger.debug("Failed to send welcome: %s", exc)

    @app.on_message(filters.left_chat_member & filters.group)
    @catch_errors
    async def track_bot_left(client: Client, message: Message):
        me = await client.get_me()
        left = message.left_chat_member

        if left and left.id == me.id:
            chat_id = message.chat.id

            # Remove group from DB
            await db.group_settings.delete_one({"chat_id": chat_id})
            logger.info("👋 Bot removed from group %s", chat_id)

            # Log to log channel
            if Config.LOG_CHANNEL:
                try:
                    await client.send_message(
                        Config.LOG_CHANNEL,
                        f"➖ Bot removed from group `{chat_id}`",
                        parse_mode="Markdown"
                    )
                except Exception as exc:
                    logger.warning("LOG_CHANNEL error: %s", exc)
