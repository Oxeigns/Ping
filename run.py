import asyncio
import logging
from pyrogram import Client
from motor.motor_asyncio import AsyncIOMotorClient

from config import Config
import handlers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    app = Client(
        "bot",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN,
    )
    app.config = Config
    app.db = AsyncIOMotorClient(Config.MONGO_URI).bot

    handlers.register_all(app)

    await app.start()
    logger.info("Bot started")
    await idle()


async def idle():
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
