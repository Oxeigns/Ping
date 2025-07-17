try:  # pragma: no cover - optional dependency
    from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
except Exception:  # pragma: no cover - define minimal stubs
    class InlineKeyboardButton:
        def __init__(self, text: str, callback_data: str | None = None) -> None:
            self.text = text
            self.callback_data = callback_data

    class InlineKeyboardMarkup(list):
        pass

from helpers.state import get_state

PREFIX = "panel:"


def abuse_status(chat_id: int) -> str:
    s = get_state(chat_id)
    on = s.text_filter or s.media_filter
    return "ON" if on else "OFF"


def main_panel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🛡 Abuse Filter", callback_data=f"{PREFIX}mod")],
            [InlineKeyboardButton("📢 Broadcast", callback_data=f"{PREFIX}broadcast")],
            [InlineKeyboardButton("📶 Status", callback_data=f"{PREFIX}stats")],
            [InlineKeyboardButton("⚙️ Settings", callback_data=f"{PREFIX}settings")],
            [InlineKeyboardButton("❓ Help", callback_data=f"{PREFIX}help")],
            [InlineKeyboardButton("👤 Developer", callback_data=f"{PREFIX}dev")],
            [InlineKeyboardButton("🚪 Exit", callback_data=f"{PREFIX}exit")],
        ]
    )


def moderation_panel(chat_id: int) -> InlineKeyboardMarkup:
    state = get_state(chat_id)
    txt = "ON" if state.text_filter else "OFF"
    med = "ON" if state.media_filter else "OFF"
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f"Text Filter: {txt}", callback_data=f"{PREFIX}text")],
            [InlineKeyboardButton(f"Media Filter: {med}", callback_data=f"{PREFIX}media")],
            [InlineKeyboardButton("🔙 Back", callback_data=f"{PREFIX}main")],
        ]
    )


def settings_panel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔙 Back", callback_data=f"{PREFIX}main")]]
    )


def admin_panel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔙 Back", callback_data=f"{PREFIX}main")]]
    )


def help_panel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔙 Back", callback_data=f"{PREFIX}main")]]
    )
