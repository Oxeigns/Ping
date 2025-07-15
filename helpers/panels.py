from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

MAX_BUTTON_TEXT = 64


def _t(text: str) -> str:
    return text if len(text) <= MAX_BUTTON_TEXT else text[:61] + "..."


PANEL_PREFIX = "panel:"  # Common prefix for callback data


def main_panel() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(_t("🗑 Text Timer"), callback_data=f"{PANEL_PREFIX}text_timer"),
            InlineKeyboardButton(_t("📷 Media Timer"), callback_data=f"{PANEL_PREFIX}media_timer"),
        ],
        [
            InlineKeyboardButton(_t("📢 Broadcast"), callback_data=f"{PANEL_PREFIX}broadcast"),
            InlineKeyboardButton(_t("🛡 Abuse Filter"), callback_data=f"{PANEL_PREFIX}abuse_filter"),
        ],
        [InlineKeyboardButton(_t("⚪ Whitelist Word"), callback_data=f"{PANEL_PREFIX}whitelist_word")],
        [InlineKeyboardButton(_t("👨‍💻 Developer Info"), url="https://t.me/samratyash32169")],
        [InlineKeyboardButton(_t("💬 Support"), url="https://t.me/+Sn1PMhrr_nIwM2Y1")],
    ]
    return InlineKeyboardMarkup(buttons)
