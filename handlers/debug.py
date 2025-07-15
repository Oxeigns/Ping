import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, TypeHandler, filters
from config import Config

logger = logging.getLogger(__name__)

def register(app: Application):
    """Debug handlers that log every incoming update."""

    async def log_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user and update.effective_user.id not in Config.SUDO_USERS:
            return
        message = update.effective_message
        if not message:
            return
        user = update.effective_user.id if update.effective_user else "unknown"
        text = message.text or message.caption or ""
        logger.info("Message from %s in %s: %s", user, update.effective_chat.id, text)

    async def log_raw(update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.debug("RAW UPDATE: %r", update)

    app.add_handler(MessageHandler(filters.ALL, log_message))
    app.add_handler(TypeHandler(Update, log_raw))

