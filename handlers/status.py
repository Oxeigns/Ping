import asyncio
import os
import psutil
from datetime import datetime
from helpers.compat import Client, Message, filters
from helpers.formatting import send_message_safe
from config import Config

START_TIME = datetime.utcnow()


def uptime() -> str:
    delta = datetime.utcnow() - START_TIME
    seconds = int(delta.total_seconds())
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours}h {minutes}m {secs}s"


def register(app: Client):
    @app.on_message(filters.command("status") & (filters.group | filters.private))
    async def status_cmd(client: Client, message: Message):
        process = psutil.Process(os.getpid())
        mem = process.memory_info().rss // (1024 * 1024)
        text = (
            f"\uD83D\uDD0C <b>Status</b>\n"
            f"Uptime: {uptime()}\n"
            f"Memory: {mem} MB"
        )
        await send_message_safe(message, text, reply_markup=None)
