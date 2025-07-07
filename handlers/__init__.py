import importlib
import pkgutil
import logging

logger = logging.getLogger(__name__)


def register_all(app):
    for loader, name, ispkg in pkgutil.iter_modules(__path__):
        module = importlib.import_module(f"{__name__}.{name}")
        if hasattr(module, "register"):
            module.register(app)
            logger.debug("Registered handler module: %s", name)
    logger.info("All handler modules registered")
