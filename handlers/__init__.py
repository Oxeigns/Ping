import importlib
import pkgutil
import logging

logger = logging.getLogger(__name__)


def register_all(app):
    for _, name, _ in pkgutil.iter_modules(__path__):
        logger.info("Loading handler: %s", name)
        module = importlib.import_module(f"{__name__}.{name}")
        if hasattr(module, "register"):
            module.register(app)
            logger.info("Handler loaded: %s", name)
        else:
            logger.warning("Module %s has no register()", name)
    logger.info("All handler modules registered")
