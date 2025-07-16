import importlib
import os
from pathlib import Path
from dotenv import load_dotenv, dotenv_values

env_path = Path(".env")
if env_path.exists():
    load_dotenv()
else:
    example = Path(".env.example")
    if example.exists():
        load_dotenv(example)
        print("[WARN] .env not found; using .env.example values")
    else:
        raise SystemExit(".env file missing and no .env.example provided")

if os.getenv("ENV") == "production" and os.getenv("CONFIRM_DEPLOY") != "yes":
    raise SystemExit(
        "Deployment aborted: set CONFIRM_DEPLOY=yes to continue in production"
    )

REQUIRED_KEYS = [
    "BOT_TOKEN",
    "API_ID",
    "API_HASH",
    "OWNER_ID",
    "LOG_CHANNEL_ID",
]

env = dotenv_values(".env") | os.environ
for key in REQUIRED_KEYS:
    if not env.get(key):
        raise SystemExit(f"Missing required env var: {key}")
if not str(env.get("API_ID", "")).isdigit():
    raise SystemExit("API_ID must be an integer")
if env.get("API_HASH") and len(env["API_HASH"]) < 30:
    raise SystemExit("API_HASH looks invalid")

try:
    from PIL import Image

    print("Pillow version", Image.__version__)
except Exception as exc:
    raise SystemExit(f"Pillow import failed: {exc}")

modules = [
    "handlers.admin",
    "handlers.panels",
    "handlers.logging",
    "handlers.moderation",
]
for name in modules:
    importlib.import_module(name)

try:  # pragma: no cover - optional dependency
    from pyrogram.handlers import MessageHandler, CallbackQueryHandler
except Exception:  # pragma: no cover - fallback stubs
    class MessageHandler:  # simple placeholders for isinstance checks
        pass

    class CallbackQueryHandler:
        pass


class DummyApp:
    def __init__(self):
        self.messages = 0
        self.callbacks = 0

    def add_handler(self, handler, group=0):
        if isinstance(handler, CallbackQueryHandler):
            self.callbacks += 1
        elif isinstance(handler, MessageHandler):
            self.messages += 1

    def on_message(self, *args, **kwargs):
        def decorator(func):
            self.messages += 1
            return func

        return decorator

    def on_callback_query(self, *args, **kwargs):
        def decorator(func):
            self.callbacks += 1
            return func

        return decorator

    def on_chat_member_updated(self, *args, **kwargs):
        def decorator(func):
            return func

        return decorator


from handlers import register_all
from handlers import moderation


def main() -> None:
    app = DummyApp()
    register_all(app)
    moderation.register(app)

    if app.messages == 0:
        raise SystemExit("message handlers not registered")

    print("Predeploy checks passed")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("Predeploy failed - rollback", exc)
        raise SystemExit(1) from exc
