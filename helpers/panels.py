try:  # Optional dependency
    from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
except Exception:
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
    return "ON" if s.text_filter or s.media_filter else "OFF"


def main_panel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛡 Abuse Filter", callback_data=f"{PREFIX}mod")],
        [InlineKeyboardButton("📢 Broadcast", callback_data=f"{PREFIX}broadcast")],
        [InlineKeyboardButton("📶 Status", callback_data=f"{PREFIX}stats")],
        [InlineKeyboardButton("🧑‍💼 Admin Commands", callback_data=f"{PREFIX}admin")],
        [InlineKeyboardButton("👤 Developer", callback_data=f"{PREFIX}dev")],
        [InlineKeyboardButton("❌ Close Panel", callback_data=f"{PREFIX}exit")],
    ])


def moderation_panel(chat_id: int) -> InlineKeyboardMarkup:
    state = get_state(chat_id)
    txt = "ON" if state.text_filter else "OFF"
    med = "ON" if state.media_filter else "OFF"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Text Filter: {txt}", callback_data=f"{PREFIX}text")],
        [InlineKeyboardButton(f"Media Filter: {med}", callback_data=f"{PREFIX}media")],
        [InlineKeyboardButton("📃 Whitelist", callback_data=f"{PREFIX}whitelist")],
        [InlineKeyboardButton("🔙 Back", callback_data=f"{PREFIX}main")],
    ])


def admin_panel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Approve", callback_data=f"{PREFIX}sendapprove")],
        [InlineKeyboardButton("⚠️ Remove Warning", callback_data=f"{PREFIX}rmwarn")],
        [InlineKeyboardButton("🚫 Unban User", callback_data=f"{PREFIX}unban")],
        [InlineKeyboardButton("🔙 Back", callback_data=f"{PREFIX}main")],
    ])


