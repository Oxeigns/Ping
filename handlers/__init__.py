import logging
from pyrogram import Client


logger = logging.getLogger(__name__)


def register_all(app: Client):
    """Import and register all Pyrogram handlers."""
    from . import (
        admin,
        autodelete,
        broadcast,
        groups,
        logging as logmod,
        moderation,
        panels,
    )

    panels.register(app)
    logger.info("[REGISTERED] panels.py ✅")
    admin.register(app)
    logger.info("[REGISTERED] admin.py ✅")
    autodelete.register(app)
    logger.info("[REGISTERED] autodelete.py ✅")
    broadcast.register(app)
    logger.info("[REGISTERED] broadcast.py ✅")
    groups.register(app)
    logger.info("[REGISTERED] groups.py ✅")
    moderation.register(app)
    logger.info("[REGISTERED] moderation.py ✅")
    logmod.register(app)
    logger.info("[REGISTERED] logging.py ✅")
