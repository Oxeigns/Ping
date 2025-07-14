import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    OWNER_ID = int(os.getenv("OWNER_ID", 0))
    LOG_CHANNEL = int(os.getenv("LOG_CHANNEL_ID", 0))
    PANEL_IMAGE = os.getenv("PANEL_IMAGE", "")
    DEV_URL = os.getenv("DEV_URL", "https://t.me/botsyard")
    DEV_NAME = os.getenv("DEV_NAME", "Developer")
