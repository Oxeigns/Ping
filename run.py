import logging
import os
import sys
import pkg_resources
from PIL import __version__ as PIL_VERSION

import aiosqlite
from pyrogram import Client, idle

import handlers
import moderation
from config import Config
from database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("Bot")

def log_versions():
    versions = {
        "Python": sys.version.split()[0],
        "Pyrogram": pkg_resources.get_distribution("pyrogram").version,
        "aiosqlite": pkg_resources.get_distribution("aiosqlite").version,
        "python-dotenv": pkg_resources.get_distribution("python-dotenv").version,
        "Pillow": PIL_VERSION,
    }
    for name, ver in versions.items():
        logger.info(f"{name} version: {ver}")

# Initialize the Pyrogram Client
app = Client(
    "bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    parse_mode="HTML",
)

async def main():
    logger.info("🚀 Bot is starting...")
    log_versions()

    # Setup SQLite DB
    db_path = Config.DATABASE_URL
    if not db_path.startswith("file:") and db_path != ":memory:":
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

    db = await aiosqlite.connect(db_path, uri=db_path.startswith("file:"))
    db.row_factory = aiosqlite.Row
    await init_db(db)
    app.db = db
    logger.info("✅ Database initialized and connected.")

    # Register handlers and moderation filters
    handlers.register_all(app)
    moderation.register(app)
    logger.info("✅ Handlers and moderation system registered.")

    if os.getenv("DEBUG_UPDATES"):
        try:
            from handlers import debug as debug_handlers
            debug_handlers.register(app)
            logger.info("🐞 Debug handlers enabled.")
        except Exception as e:
            logger.exception("Failed to register debug handlers: %s", e)

    async with app:
        logger.info("🤖 Bot started. Waiting for updates...")
        await idle()

    await db.close()
    logger.info("📴 Database connection closed.")

if __name__ == "__main__":
    try:
        logger.info("🔧 Launching bot process...")
        import asyncio
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.warning("⚠️ Bot shutdown via keyboard or system exit.")
    except Exception as e:
        logger.exception("❌ Unhandled exception in bot: %s", e)
