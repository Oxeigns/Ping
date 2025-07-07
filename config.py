import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration loaded from .env"""

    API_ID = int(os.getenv("API_ID", "0"))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")

    OWNER_ID = int(os.getenv("OWNER_ID", "0"))
    LOG_CHANNEL = int(os.getenv("LOG_CHANNEL_ID", "0"))

    PERSPECTIVE_API_KEY = os.getenv("PERSPECTIVE_API_KEY", "")
    IMAGE_MOD_API_KEY = os.getenv("IMAGE_MOD_API_KEY", "")

    DATABASE_URL = os.getenv("DATABASE_URL", "bot.db")

    _sight = IMAGE_MOD_API_KEY.split(":", 1)
    SIGHTENGINE_USER = _sight[0] if _sight else ""
    SIGHTENGINE_SECRET = _sight[1] if len(_sight) > 1 else ""
