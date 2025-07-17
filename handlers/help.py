from helpers.compat import Client, Message, filters
from helpers.formatting import send_message_safe
from texts import HELP_TEXT


def register(app: Client):
    @app.on_message(filters.command("help") & (filters.group | filters.private))
    async def help_cmd(_: Client, message: Message):
        await send_message_safe(message, HELP_TEXT)
