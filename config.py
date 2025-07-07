import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    """Configuration loaded from environment variables."""

    API_ID = int(os.getenv("API_ID", "0"))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    # DATABASE_URL is preferred but fall back to legacy MONGO_URI
    MONGO_URI = os.getenv("DATABASE_URL", os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    LOG_CHANNEL = int(os.getenv("LOG_CHANNEL_ID", "0"))
    OWNER_ID = int(os.getenv("OWNER_ID", "0"))
    # TOXICITY_API_KEY is preferred but fall back to legacy PERSPECTIVE_API_KEY
    PERSPECTIVE_API_KEY = os.getenv("TOXICITY_API_KEY", os.getenv("PERSPECTIVE_API_KEY", ""))
    SIGHTENGINE_USER = os.getenv("SIGHTENGINE_USER", "")
    SIGHTENGINE_SECRET = os.getenv("SIGHTENGINE_SECRET", "")
