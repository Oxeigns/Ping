import asyncio
import aiosqlite
from telegram.ext import ApplicationBuilder

from config import Config
from database import init_db
from handlers.start import register as register_start
from handlers.admin import register as register_admin
from handlers.debug import register as register_debug
from moderation import register as register_moderation


async def post_init(application):
    application.db = await aiosqlite.connect(Config.DATABASE_URL)
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
