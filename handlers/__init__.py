import logging

logger = logging.getLogger(__name__)


def register_all(app):
    """Import and register all handler modules."""
    from . import start, admin, debug, moderation

    start.register(app)
    admin.register(app)
    debug.register(app)
    moderation.register(app)

    logger.info("🎉 All handler modules registered successfully.")
