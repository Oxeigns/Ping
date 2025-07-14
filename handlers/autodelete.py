import asyncio
import contextlib
from pyrogram import Client, filters
from pyrogram.types import Message
from helpers.mongo import get_db


def register(app: Client):
    db = get_db()

    async def schedule_delete(message: Message, delay: int):
        await asyncio.sleep(delay)
        with contextlib.suppress(Exception):
            await message.delete()

    @app.on_message(filters.group)
    async def auto_delete(client: Client, message: Message):
        await db.group_settings.update_one(
            {"chat_id": message.chat.id},
            {"$setOnInsert": {"chat_id": message.chat.id}},
            upsert=True,
        )
        settings = await db.group_settings.find_one({"chat_id": message.chat.id}) or {}
        if message.media:
            delay = settings.get("media_timer")
        else:
            delay = settings.get("text_timer")
        if delay:
            asyncio.create_task(schedule_delete(message, int(delay)))
