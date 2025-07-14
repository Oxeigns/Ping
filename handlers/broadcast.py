from pyrogram import Client, filters
from pyrogram.types import Message
from helpers.mongo import get_db
from config import Config


def register(app: Client):
    db = get_db()

    @app.on_message(filters.command("broadcast") & filters.user(Config.OWNER_ID))
    async def broadcast(client: Client, message: Message):
        if len(message.command) < 2:
            await message.reply_text(
                "❌ Usage: /broadcast <text>",
                quote=True,
            )
            return
        text = message.text.split(None, 1)[1]
        sent = 0
        async for chat in db.group_settings.find({}, {"chat_id": 1}):
            try:
                await client.send_message(chat["chat_id"], text)
                sent += 1
            except Exception:
                continue
        await message.reply_text(
            f"✅ Broadcast sent to {sent} chats",
            quote=True,
        )

    @app.on_message(filters.command("broadcast") & ~filters.user(Config.OWNER_ID))
    async def no_broadcast(_: Client, message: Message):
        await message.reply_text(
            "❌ Only the bot owner can broadcast messages.",
            quote=True,
        )
