import functools
import logging
from pyrogram.types import Message

logger = logging.getLogger(__name__)


def require_admin(func):
    @functools.wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        from .perms import is_admin
        if not await is_admin(client, message):
            await message.reply_text("Admins only")
            return
        return await func(client, message, *args, **kwargs)

    return wrapper


def catch_errors(func):
    @functools.wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        try:
            return await func(client, message, *args, **kwargs)
        except Exception as e:
            logger.exception("Handler error: %s", e)
            await message.reply_text("An error occurred")
    return wrapper
