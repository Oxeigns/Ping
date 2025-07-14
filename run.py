import asyncio
import logging
from pyrogram import Client, idle
from config import Config
from helpers.mongo import connect
from handlers import register_all


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


async def main():
    logger.info("[INFO] Connecting to MongoDB...")
    db = await connect(Config.MONGO_URI)
    logger.info("[INFO] Initializing bot...")
    app = Client(
        "bot",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN,
    )
    app.db = db
    register_all(app)
    logger.info("[READY] Command handlers active")
    await app.start()
    logger.info("[READY] Bot is now live ✅")
    await idle()
    await app.stop()


if __name__ == "__main__":
    asyncio.run(main())
