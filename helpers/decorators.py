import functools
import logging
from contextlib import suppress
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

def catch_errors(func):
    """
    Decorator for safely catching and logging exceptions in async handlers.
    """
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            logger.exception("❌ Error in handler %s: %s", func.__name__, e)
            # Optional: You can also notify in dev channel or reply in chat
            if update.message:
                with suppress(Exception):
                    await update.message.reply_text("⚠️ An internal error occurred. Please try again later.")
    return wrapper

