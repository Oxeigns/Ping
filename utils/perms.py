from pyrogram.types import Message


def is_owner(user_id: int, owner_id: int) -> bool:
    return user_id == owner_id


async def is_admin(message: Message) -> bool:
    if not message.chat or not message.from_user:
        return False
    member = await message.chat.get_member(message.from_user.id)
    return member.status in ("administrator", "creator")
