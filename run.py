import asyncio
import os
import aiosqlite
from telegram.ext import ApplicationBuilder

from config import Config
from database import init_db
from handlers.start import register as register_start
from handlers.admin import register as register_admin
from handlers.debug import register as register_debug
from moderation import register as register_moderation


async def post_init(application):
    db_url = Config.DATABASE_URL
    if "://" not in db_url and db_url not in ("", ":memory:"):
        db_dir = os.path.dirname(db_url)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    uri = db_url.startswith("file:")
    application.db = await aiosqlite.connect(db_url, uri=uri)
    await init_db(application.db)


def main() -> None:
    application = (
        ApplicationBuilder()
        .token(Config.BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    register_start(application)
    register_admin(application)
    register_debug(application)
    register_moderation(application)

    application.run_polling()


if __name__ == "__main__":
    main()
