import asyncio
import logging
import os
import aiosqlite
from telegram.ext import ApplicationBuilder, ContextTypes
from telegram.error import Conflict

from config import Config
from database import init_db
from handlers.start import register as register_start
from handlers.admin import register as register_admin
from handlers.debug import register as register_debug
from moderation import register as register_moderation


async def post_init(application):
    db_url = Config.DATABASE_URL

    # Extract filesystem path from "file:" URLs so we can create directories
    if db_url.startswith("file:"):
        from urllib.parse import urlparse, unquote

        parsed = urlparse(db_url)
        db_path = unquote(parsed.path or parsed.netloc)
        uri = True
    else:
        db_path = db_url
        uri = False

    # Create directory for SQLite database if needed
    if db_path not in ("", ":memory:"):
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    application.db = await aiosqlite.connect(db_url, uri=uri)
    await init_db(application.db)

    try:
        await application.bot.delete_webhook(drop_pending_updates=True)
    except Exception as exc:
        logging.warning("Failed to delete webhook: %s", exc)


def main() -> None:
    application = (
        ApplicationBuilder()
        .token(Config.BOT_TOKEN)
        .post_init(post_init)
        .build()
    )
    application.config = Config

    register_start(application)
    register_admin(application)
    register_debug(application)
    register_moderation(application)

    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        if isinstance(context.error, Conflict):
            logging.warning("Telegram API conflict: %s", context.error)
            return
        logging.exception("Unhandled exception: %s", context.error)

    application.add_error_handler(error_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
