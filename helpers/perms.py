from pyrogram import Client, filters
from pyrogram.types import Message

async def is_admin(client: Client, message: Message) -> bool:
    if not message.chat or not message.from_user:
        return False
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    return member.status in ("administrator", "creator")
