import logging
from pyrogram import filters
from pyrogram.types import Update

logger = logging.getLogger(__name__)

def register(app):
    """Debug handlers that log every incoming update."""

    @app.on_message(filters.all)
    async def log_message(client, message):
        user = message.from_user.id if message.from_user else 'unknown'
        text = message.text or message.caption or ''
        logger.info("Message from %s in %s: %s", user, message.chat.id, text)

    @app.on_raw_update()
    async def log_raw(client, update: Update, users, chats):
        logger.debug("RAW UPDATE: %r", update)
