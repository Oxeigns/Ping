import logging
from helpers.compat import Client, Message, filters
from config import Config

logger = logging.getLogger(__name__)


def register(app: Client) -> None:
    """Attach simple update logging handlers."""

    @app.on_message(filters.all & filters.user(list(Config.SUDO_USERS)))
    async def log_message(client: Client, message: Message) -> None:
        text = message.text or message.caption or ""
        user = message.from_user.id if message.from_user else "unknown"
        chat = message.chat.id if message.chat else "private"
        logger.info("Message from %s in %s: %s", user, chat, text)
