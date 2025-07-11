import os
import logging
from urllib.parse import urlparse, unquote
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

    PANEL_IMAGE = os.getenv("PANEL_IMAGE")
    DEV_URL = os.getenv("DEV_URL", "https://t.me/Oxeign")

    # Prefer DB_FILE to avoid clashing with hosting providers that predefine
    # DATABASE_URL for Postgres connections (e.g. Render.com). Fallback to
    # DATABASE_URL if provided and looks like a file path.
    _db_file = os.getenv("DB_FILE") or None
    _db_url = os.getenv("DATABASE_URL")

    if not _db_url:
        _db_url = "bot.db"

    if _db_file:
        DATABASE_URL = _db_file
    elif _db_url.startswith("postgres://") or _db_url.startswith("postgresql://"):
        logger.warning(
            "Ignoring external DATABASE_URL=%s; using local SQLite db. "
            "Set DB_FILE to override.",
            _db_url,
        )
        DATABASE_URL = "bot.db"
    elif _db_url.startswith("sqlite:"):
        parsed = urlparse(_db_url)
        path = unquote(parsed.path or parsed.netloc)
        DATABASE_URL = f"file:{path}?{parsed.query}" if parsed.query else path
    else:
        DATABASE_URL = _db_url

    # When using a relative SQLite path on read-only filesystems (e.g. Render),
    # fall back to a writable location under /tmp.
    if "://" not in DATABASE_URL and DATABASE_URL not in ("", ":memory:"):
        db_dir = os.path.dirname(DATABASE_URL) or "."
        if not os.access(db_dir, os.W_OK):
            base = os.path.basename(DATABASE_URL) or "bot.db"
            tmp_path = os.path.join("/tmp", base)
            logger.warning(
                "DB path %s not writable; using %s instead", DATABASE_URL, tmp_path
            )
            DATABASE_URL = tmp_path

