import asyncio
import logging

import aiosqlite
from pyrogram import Client

import handlers
import moderation
from database import init_db
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    app = Client(
        "bot",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN,
    )

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
