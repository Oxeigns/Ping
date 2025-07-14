from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


PANEL_PREFIX = "panel:"  # Common prefix for callback data


def main_panel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🗑 Text Timer", callback_data=f"{PANEL_PREFIX}text_timer"
                )
            ],
            [
                InlineKeyboardButton(
                    "📷 Media Timer", callback_data=f"{PANEL_PREFIX}media_timer"
                )
            ],
            [
                InlineKeyboardButton(
                    "📢 Broadcast", callback_data=f"{PANEL_PREFIX}broadcast"
                )
            ],
            [
                InlineKeyboardButton(
                    "🛡 Abuse Filter", callback_data=f"{PANEL_PREFIX}abuse_filter"
                )
            ],
            [
                InlineKeyboardButton(
                    "⚪ Whitelist Word", callback_data=f"{PANEL_PREFIX}whitelist_word"
                )
            ],
            [InlineKeyboardButton("👨‍💻 Developer Info", url="https://t.me/samratyash32169")],
            [InlineKeyboardButton("💬 Support", url="https://t.me/+Sn1PMhrr_nIwM2Y1")],
        ]
    )
