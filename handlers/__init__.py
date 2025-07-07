import importlib
import pkgutil


def register_all(app):
    for loader, name, ispkg in pkgutil.iter_modules(__path__):
        module = importlib.import_module(f"{__name__}.{name}")
        if hasattr(module, "register"):
            module.register(app)
