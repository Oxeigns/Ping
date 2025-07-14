import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from helpers.mongo import get_db
from config import Config


def register(app: Client):
    logger = logging.getLogger(__name__)
    db = get_db()

    @app.on_message(
        filters.command("broadcast")
        & (filters.group | filters.private)
        & filters.user(Config.OWNER_ID)
    )
    async def broadcast(client: Client, message: Message):
        if message.reply_to_message:
            target = message.reply_to_message
        elif len(message.command) > 1:
            target = message
        else:
            await message.reply_text(
                "❌ Usage: reply or `/broadcast <text>`",
                quote=True,
            )
            return

        sent = 0
        async for chat in db.group_settings.find({}, {"chat_id": 1}):
            chat_id = chat.get("chat_id")
            try:
                if target is message:
                    await client.send_message(chat_id, message.text.split(None, 1)[1])
                else:
                    await target.copy(chat_id)
                logger.info("[SENT] %s", chat_id)
                sent += 1
            except Exception as e:
                logger.warning("[FAILED] %s: %s", chat_id, e)
        await message.reply_text(
            f"✅ Broadcast complete to {sent} chats",
            quote=True,
        )

    @app.on_message(
        filters.command("broadcast")
        & (filters.group | filters.private)
        & ~filters.user(Config.OWNER_ID)
    )
    async def no_broadcast(_: Client, message: Message):
        await message.reply_text(
            "❌ Only the bot owner can broadcast messages.",
            quote=True,
        )
