import logging
from pyrogram import Client


logger = logging.getLogger(__name__)


def register_all(app: Client):
    from . import start, admin, autodelete, broadcast

    start.register(app)
    logger.info("[LOADED] start.py registered")
    admin.register(app)
    logger.info("[LOADED] admin.py registered")
    autodelete.register(app)
    logger.info("[LOADED] autodelete.py registered")
    broadcast.register(app)
    logger.info("[LOADED] broadcast.py registered")
