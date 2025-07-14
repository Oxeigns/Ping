import functools
import logging
from pyrogram.types import Message

logger = logging.getLogger(__name__)


def require_admin(func):
    @functools.wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        from .perms import is_admin
        from config import Config

        if message.from_user and message.from_user.id == Config.OWNER_ID:
            return await func(client, message, *args, **kwargs)

        if not await is_admin(client, message):
            await message.reply_text(
                "❌ You need to be an admin to use this command.",
                quote=True,
            )
            return

        return await func(client, message, *args, **kwargs)

    return wrapper


def require_owner(func):
    @functools.wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        from .perms import is_owner
        from config import Config

        if message.from_user and message.from_user.id == Config.OWNER_ID:
            return await func(client, message, *args, **kwargs)

        if not await is_owner(client, message):
            await message.reply_text(
                "❌ Only the group owner can use this command.",
                quote=True,
            )
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
            await message.reply_text("❌ An unexpected error occurred.")
    return wrapper
