from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus

async def is_admin(client: Client, message: Message) -> bool:
    if not message.chat or not message.from_user:
        return False
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)


async def is_owner(client: Client, message: Message) -> bool:
    """Return ``True`` if the user is the chat owner."""
    if not message.chat or not message.from_user:
        return False
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    return member.status == ChatMemberStatus.OWNER
