import importlib
import pkgutil
import logging

logger = logging.getLogger(__name__)

def register_all(app):
    """Dynamically imports and registers all handler modules in the current package."""
    for _, name, ispkg in pkgutil.iter_modules(__path__):
        if ispkg:
            continue  # skip sub-packages

        module_path = f"{__name__}.{name}"
        try:
            logger.info(f"🔄 Importing handler: {module_path}")
            module = importlib.import_module(module_path)

            if hasattr(module, "register") and callable(module.register):
                module.register(app)
                logger.info(f"✅ Registered handler: {name}")
            else:
                logger.warning(f"⚠️ Module '{name}' does not define a `register(app)` function.")
        except Exception as e:
            logger.exception(f"❌ Failed to load module '{name}': {e}")

    logger.info("🎉 All handler modules registered successfully.")
