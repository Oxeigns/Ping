import asyncio
import logging
import sys
import pkg_resources
from PIL import __version__ as PIL_VERSION

import aiosqlite
from pyrogram import Client

import handlers
import moderation
from database import init_db
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def log_versions():
    versions = {
        "python": sys.version.split()[0],
        "pyrogram": pkg_resources.get_distribution("pyrogram").version,
        "aiosqlite": pkg_resources.get_distribution("aiosqlite").version,
        "python-dotenv": pkg_resources.get_distribution("python-dotenv").version,
        "pillow": PIL_VERSION,
    }
    for name, ver in versions.items():
        logger.info("%s version: %s", name, ver)


async def main():
    app = Client(
        "bot",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN,
    )

    log_versions()

    db = await aiosqlite.connect(Config.DATABASE_URL)
    db.row_factory = aiosqlite.Row
    await init_db(db)
    app.db = db

    await app.start()
    logger.info("Bot started")
    handlers.register_all(app)
    moderation.register(app)
    await idle()


async def idle():
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
