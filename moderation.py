from pyrogram import filters
from pyrogram.types import Message, ChatPermissions

from utils import add_warning, catch_errors, check_toxicity

BANNED_WORDS = {"badword", "hate"}
TOXICITY_THRESHOLD = 0.8
WARN_THRESHOLD = 3


def register(app):
    @app.on_message(filters.text & ~filters.private)
    @catch_errors
    async def text_moderation(client, message: Message):
        if not message.from_user or message.from_user.is_self:
            return
        text = message.text.lower()
        if any(word in text for word in BANNED_WORDS):
            toxicity = 1.0
        else:
            toxicity = await check_toxicity(text)

        if toxicity >= TOXICITY_THRESHOLD:
            user = await add_warning(app.db, message.from_user.id, toxicity)
            if user["warnings"] >= WARN_THRESHOLD:
                await message.chat.restrict(message.from_user.id, ChatPermissions())
                await message.reply_text("User muted for repeated violations.")
            else:
                await message.reply_text(
                    f"Toxicity {toxicity:.2f}. Please keep the chat civil."
                )
