import logging
import os
import sys
import pkg_resources
from PIL import __version__ as PIL_VERSION
from dotenv import load_dotenv

import aiosqlite
from pyrogram import Client
import asyncio

import handlers
import moderation
load_dotenv()
from config import Config
from database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("Bot")

if not all([Config.BOT_TOKEN, Config.API_ID, Config.API_HASH]):
    missing = [
        name
        for name, value in {
            "BOT_TOKEN": Config.BOT_TOKEN,
            "API_ID": Config.API_ID,
            "API_HASH": Config.API_HASH,
        }.items()
        if not value
    ]
    logger.error("Missing required environment variables: %s", ", ".join(missing))
    raise SystemExit(1)

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

    logger.info("🔐 Using BOT_TOKEN: %s...", Config.BOT_TOKEN[:10])
    logger.info("🛰️ Connecting to Telegram...")

    # Setup SQLite DB
    db_path = Config.DATABASE_URL
    if not db_path.startswith("file:") and db_path != ":memory:":
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

    db = await aiosqlite.connect(db_path, uri=db_path.startswith("file:"))
    db.row_factory = aiosqlite.Row
    await init_db(db)
    app.db = db
    logger.info("✅ Database initialized and connected.")

    # Register handlers
    handlers.register_all(app)
    logger.info("✅ Handlers registered.")

    # Register moderation
    moderation.register(app)
    logger.info("✅ Moderation registered.")

    if os.getenv("DEBUG_UPDATES"):
        try:
            from handlers import debug as debug_handlers
            debug_handlers.register(app)
            logger.info("🐞 Debug handlers enabled.")
        except Exception as e:
            logger.exception("Failed to register debug handlers: %s", e)

    try:
        await app.start()
        logger.info("✅ Connected to Telegram successfully.")
    except Exception as e:
        logger.exception("❌ Failed to connect to Telegram: %s", e)
        raise

    logger.info("🤖 Bot started. Waiting for updates...")
    try:
        await app.idle()
    except asyncio.CancelledError:
        logger.info("Stop signal received (SIGINT). Exiting...")
        raise
    finally:
        await app.stop()
        await db.close()
        logger.info("📴 Database connection closed.")

if __name__ == "__main__":
    asyncio.run(main())
