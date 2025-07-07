import logging
from pyrogram.types import Message

logger = logging.getLogger(__name__)

async def safe_edit(message: Message, text: str, **kwargs):
    """
    Safely edits a Telegram message with error handling.
    """
    try:
        await message.edit_text(text, **kwargs)
    except Exception as e:
        logger.warning("❗ Failed to edit message %s: %s", message.id, e)
