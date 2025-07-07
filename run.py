import asyncio
import os
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


app = Client(
    "bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    parse_mode="HTML",
)


async def main():
    logger.info("Bot started")
    log_versions()

    db_path = Config.DATABASE_URL
    if not db_path.startswith("file:") and db_path != ":memory:":
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    db = await aiosqlite.connect(db_path, uri=db_path.startswith("file:"))
    db.row_factory = aiosqlite.Row
    await init_db(db)
    app.db = db

    handlers.register_all(app)
    moderation.register(app)
    logger.debug("Handlers and moderation registered")

    await asyncio.Event().wait()


if __name__ == "__main__":
    logger.info("Starting bot")
    app.run(main())
