from datetime import datetime
import os
import psutil
from helpers.compat import Client, Message, filters
from helpers.formatting import send_message_safe

START_TIME = datetime.utcnow()

def uptime() -> str:
    delta = datetime.utcnow() - START_TIME
    total_seconds = int(delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"

def register(app: Client):
    @app.on_message(filters.command("status") & (filters.group | filters.private))
    async def status_cmd(client: Client, message: Message):
        try:
            mem = psutil.Process(os.getpid()).memory_info().rss // (1024 * 1024)
        except Exception:
            mem = "N/A"

        me = await client.get_me()
        text = (
            f"🔌 <b>Bot Status</b>\n"
            f"⏱ <b>Uptime:</b> <code>{uptime()}</code>\n"
            f"🧠 <b>Memory:</b> <code>{mem} MB</code>\n"
            f"🤖 <b>Bot:</b> <code>@{me.username}</code>"
        )
        await send_message_safe(message, text)
