from pyrogram import Client, filters
from pyrogram.types import Message
from helpers.decorators import require_admin, require_owner
from helpers.mongo import get_db
from helpers.abuse import add_word, remove_word
from config import Config


def register(app: Client):
    db = get_db()

    @app.on_message(
        filters.command("set_text_timer") & (filters.group | filters.private)
    )
    @require_admin
    async def set_text(client: Client, message: Message):
        if len(message.command) < 2 or not message.command[1].isdigit():
            await message.reply_text(
                "❌ Usage: /set_text_timer <seconds>",
                quote=True,
            )
            return
        seconds = int(message.command[1])
        await db.group_settings.update_one(
            {"chat_id": message.chat.id},
            {"$set": {"text_timer": seconds}},
            upsert=True,
        )
        await message.reply_text(
            f"✅ Text messages will be deleted after {seconds}s",
            quote=True,
        )

    @app.on_message(
        filters.command("set_media_timer") & (filters.group | filters.private)
    )
    @require_admin
    async def set_media(client: Client, message: Message):
        if len(message.command) < 2 or not message.command[1].isdigit():
            await message.reply_text(
                "❌ Usage: /set_media_timer <seconds>",
                quote=True,
            )
            return
        seconds = int(message.command[1])
        await db.group_settings.update_one(
            {"chat_id": message.chat.id},
            {"$set": {"media_timer": seconds}},
            upsert=True,
        )
        await message.reply_text(
            f"✅ Media will be deleted after {seconds}s",
            quote=True,
        )

    @app.on_message(
        filters.command("addabuse")
        & (filters.group | filters.private)
        & filters.user(Config.OWNER_ID)
    )
    async def add_abuse(client: Client, message: Message):
        if len(message.command) < 2:
            await message.reply_text(
                "❌ Usage: /addabuse <word>",
                quote=True,
            )
            return
        await add_word(message.command[1])
        await message.reply_text("✅ Word added.", quote=True)

    @app.on_message(
        filters.command("removeabuse")
        & (filters.group | filters.private)
        & filters.user(Config.OWNER_ID)
    )
    async def remove_abuse(client: Client, message: Message):
        if len(message.command) < 2:
            await message.reply_text(
                "❌ Usage: /removeabuse <word>",
                quote=True,
            )
            return
        await remove_word(message.command[1])
        await message.reply_text("✅ Word removed.", quote=True)

    @app.on_message(filters.command("whitelist") & filters.group)
    @require_owner
    async def whitelist_word(client: Client, message: Message):
        if len(message.command) < 2:
            await message.reply_text(
                "❌ Usage: /whitelist <word>",
                quote=True,
            )
            return
        word = message.command[1].lower()
        await db.group_settings.update_one(
            {"chat_id": message.chat.id},
            {"$addToSet": {"whitelist": word}, "$setOnInsert": {"chat_id": message.chat.id}},
            upsert=True,
        )
        await message.reply_text("✅ Word whitelisted in this group.", quote=True)

    @app.on_message(filters.command("removewhitelist") & filters.group)
    @require_owner
    async def remove_whitelist_word(client: Client, message: Message):
        if len(message.command) < 2:
            await message.reply_text(
                "❌ Usage: /removewhitelist <word>",
                quote=True,
            )
            return
        word = message.command[1].lower()
        await db.group_settings.update_one(
            {"chat_id": message.chat.id},
            {"$pull": {"whitelist": word}},
            upsert=True,
        )
        await message.reply_text("✅ Word removed from whitelist.", quote=True)
