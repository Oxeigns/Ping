from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_panel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🗑 Text Timer", callback_data="set_text")],
            [InlineKeyboardButton("📷 Media Timer", callback_data="set_media")],
            [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")],
            [InlineKeyboardButton("🛡 Abuse Filter", callback_data="abuse")],
            [InlineKeyboardButton("🧑‍💻 Developer Info", callback_data="dev")],
            [InlineKeyboardButton("💬 Support", callback_data="support")],
        ]
    )
