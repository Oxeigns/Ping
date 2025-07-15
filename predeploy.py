import importlib
import os
from dotenv import load_dotenv

load_dotenv()

if os.getenv("ENV") == "production" and os.getenv("CONFIRM_DEPLOY") != "yes":
    raise SystemExit("Deployment aborted: set CONFIRM_DEPLOY=yes to continue in production")

REQUIRED_KEYS = [
    "BOT_TOKEN",
    "API_ID",
    "API_HASH",
    "OWNER_ID",
    "LOG_CHANNEL_ID",
]

for key in REQUIRED_KEYS:
    if not os.getenv(key):
        raise SystemExit(f"Missing required env var: {key}")

try:
    from PIL import Image
    print("Pillow version", Image.__version__)
except Exception as exc:
    raise SystemExit(f"Pillow import failed: {exc}")

modules = [
    "handlers.admin",
    "handlers.start",
    "handlers.debug",
    "handlers.moderation",
]
for name in modules:
    importlib.import_module(name)

from pyrogram.handlers import MessageHandler, CallbackQueryHandler


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

app = DummyApp()
register_all(app)
moderation.register(app)

if app.messages == 0:
    raise SystemExit("message handlers not registered")

print("Predeploy checks passed")
