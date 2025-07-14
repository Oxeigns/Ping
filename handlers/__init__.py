import logging
from pyrogram import Client


logger = logging.getLogger(__name__)


def register_all(app: Client):
    """Import and register all Pyrogram handlers."""
    from . import start, admin, autodelete, broadcast

    start.register(app)
    logger.info("[REGISTERED] start.py")
    admin.register(app)
    logger.info("[REGISTERED] admin.py")
    autodelete.register(app)
    logger.info("[REGISTERED] autodelete.py")
    broadcast.register(app)
    logger.info("[REGISTERED] broadcast.py")
