import logging
from helpers.compat import Client


logger = logging.getLogger(__name__)


def register_all(app: Client):
    """Import and register all Pyrogram handlers."""
    from . import (
        admin,
        autodelete,
        broadcast,
        groups,
        activity_log as logmod,
        moderation,
        panels,
        status,
        help as helpmod,
    )

    panels.register(app)
    logger.info("[REGISTERED] panels.py ✅")
    admin.register(app)
    logger.info("[REGISTERED] admin.py ✅")
    autodelete.register(app)
    logger.info("[REGISTERED] autodelete.py ✅")
    broadcast.register(app)
    logger.info("[REGISTERED] broadcast.py ✅")
    helpmod.register(app)
    logger.info("[REGISTERED] help.py ✅")
    groups.register(app)
    logger.info("[REGISTERED] groups.py ✅")
    moderation.register(app)
    logger.info("[REGISTERED] moderation.py ✅")
    status.register(app)
    logger.info("[REGISTERED] status.py ✅")
    logmod.register(app)
    logger.info("[REGISTERED] activity_log.py ✅")
