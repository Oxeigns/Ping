import logging
from telegram import Message
from telegram.constants import ChatMemberStatus

logger = logging.getLogger(__name__)


def is_owner(user_id: int, owner_id: int) -> bool:
    """
    Check if the user is the bot owner.
    """
    return user_id == owner_id


async def is_admin(message: Message) -> bool:
    """
    Check if the message sender is an admin in the chat.
    """
    if not message.chat or not message.from_user:
        return False

    try:
        member = await message.chat.get_member(message.from_user.id)
        return member.status in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER,
        )
    except Exception as e:
        logger.warning("⚠️ Failed to check admin status for user %s: %s", message.from_user.id, e)
        return False
