import asyncio
import logging
from helpers.compat import Client
try:  # pragma: no cover - optional pyrogram dependency
    from pyrogram import idle  # type: ignore
except Exception:  # pragma: no cover - stub when pyrogram missing
    async def idle() -> None:
        """Placeholder idle when Pyrogram is unavailable."""
        await asyncio.Event().wait()
from config import Config, validate
from helpers.mongo import connect
from handlers import register_all


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


async def main():
    validate()
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
    logger.info("[REGISTERED] all handler modules")
    logger.info("[READY] Command handlers active")
    await app.start()
    logger.info("[READY] Bot is now live ✅")
    await idle()
    await app.stop()


if __name__ == "__main__":
    asyncio.run(main())
