from pyrogram.types import Message


async def safe_edit(message: Message, text: str, **kwargs):
    try:
        await message.edit_text(text, **kwargs)
    except Exception:
        pass
