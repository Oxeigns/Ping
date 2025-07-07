import functools
import logging
from pyrogram.types import Message

logger = logging.getLogger(__name__)


def catch_errors(func):
    @functools.wraps(func)
    async def wrapper(client, message: Message):
        try:
            return await func(client, message)
        except Exception as e:
            logger.exception("Handler error: %s", e)
    return wrapper
