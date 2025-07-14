from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_panel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🗑 Text Timer", callback_data="text_timer")],
            [InlineKeyboardButton("📷 Media Timer", callback_data="media_timer")],
            [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast_panel")],
            [InlineKeyboardButton("🛡 Abuse Filter", callback_data="abuse_panel")],
            [
                InlineKeyboardButton(
                    "🧑‍💻 Developer Info", url="https://t.me/samratyash32169"
                )
            ],
            [
                InlineKeyboardButton(
                    "💬 Support", url="https://t.me/+Sn1PMhrr_nIwM2Y1"
                )
            ],
        ]
    )
