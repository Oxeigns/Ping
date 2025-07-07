import os
import logging
from dotenv import load_dotenv

load_dotenv()


logger = logging.getLogger(__name__)


class Config:
    """Configuration loaded from .env"""

    API_ID = int(os.getenv("API_ID", "0"))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")

    OWNER_ID = int(os.getenv("OWNER_ID", "1888832817"))

    _log_id = os.getenv("LOG_CHANNEL_ID", "-1002867268050")
    try:
        LOG_CHANNEL = int(_log_id)
    except ValueError:
        LOG_CHANNEL = -1002867268050
        logger.warning("Invalid LOG_CHANNEL_ID %r, falling back to %d", _log_id, LOG_CHANNEL)

    PERSPECTIVE_API_KEY = os.getenv("PERSPECTIVE_API_KEY", "")
    IMAGE_MOD_API_KEY = os.getenv("IMAGE_MOD_API_KEY", "")

    DATABASE_URL = os.getenv("DATABASE_URL", "bot.db")

    _sight = IMAGE_MOD_API_KEY.split(":", 1)
    SIGHTENGINE_USER = _sight[0] if _sight else ""
    SIGHTENGINE_SECRET = _sight[1] if len(_sight) > 1 else ""
