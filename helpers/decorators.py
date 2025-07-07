import functools
import logging
from contextlib import suppress
from pyrogram.types import Message
from pyrogram.client import Client

logger = logging.getLogger(__name__)

def catch_errors(func):
    """
    Decorator for safely catching and logging exceptions in async Pyrogram handlers.
    """
    @functools.wraps(func)
    async def wrapper(client: Client, *args, **kwargs):
        try:
            return await func(client, *args, **kwargs)
        except Exception as e:
            logger.exception(f"❌ Error in handler {func.__name__}: {e}")
            # Optional: You can also notify in dev channel or reply in chat
            if args and isinstance(args[0], Message):
                with suppress(Exception):
                    await args[0].reply_text("⚠️ An internal error occurred. Please try again later.")
    return wrapper
