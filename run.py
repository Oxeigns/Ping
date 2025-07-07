import asyncio
import logging
from pyrogram import Client
from motor.motor_asyncio import AsyncIOMotorClient

from config import Config
import handlers
import moderation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    app = Client(
        "bot",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN,
        plugins=None,
    )

    db = AsyncIOMotorClient(Config.MONGO_URI).bot
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
