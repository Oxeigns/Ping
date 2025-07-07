from pyrogram import filters
from pyrogram.types import Message, ChatPermissions

from utils import api, db, perms, logger, errors

BANNED_WORDS = {"badword", "hate"}
WARNING_LIMIT = 3


def register(app):
    @app.on_message(filters.text & ~filters.private)
    @errors.catch_errors
    async def check_text(client, message: Message):
        if not message.from_user or await perms.is_admin(message):
            return
        user = await db.get_user(app.db, message.from_user.id)
        if int(message.chat.id) in user.get("approved_in", []):
            return
        text = message.text or ""
        if any(word in text.lower() for word in BANNED_WORDS):
            toxicity = await api.check_text_toxicity(text)
            warnings = await db.add_warning(app.db, message.chat.id, message.from_user.id, int(toxicity))
            await logger.log_action(app, f"Warned {message.from_user.id} in {message.chat.id}. warnings={warnings}")
            if warnings >= WARNING_LIMIT:
                await message.chat.restrict(message.from_user.id, ChatPermissions())
                await logger.log_action(app, f"Muted {message.from_user.id} in {message.chat.id}")
            await message.delete()

    @app.on_message((filters.photo | filters.sticker) & ~filters.private)
    @errors.catch_errors
    async def check_media(client, message: Message):
        if not message.from_user or await perms.is_admin(message):
            return
        user = await db.get_user(app.db, message.from_user.id)
        if int(message.chat.id) in user.get("approved_in", []):
            return
        if message.photo:
            file = await message.download()
            result = await api.check_image(file)
            if result.get("flagged"):
                warnings = await db.add_warning(app.db, message.chat.id, message.from_user.id, 10)
                await logger.log_action(app, f"Image violation by {message.from_user.id} in {message.chat.id}")
                if warnings >= WARNING_LIMIT:
                    await message.chat.restrict(message.from_user.id, ChatPermissions())
                await message.delete()
