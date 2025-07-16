try:  # pragma: no cover - optional dependency
    from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
except Exception:  # pragma: no cover - define minimal stubs
    class InlineKeyboardButton:
        def __init__(self, text: str, callback_data: str | None = None) -> None:
            self.text = text
            self.callback_data = callback_data

    class InlineKeyboardMarkup(list):
        pass

PREFIX = "panel:"


def main_panel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🛡 Moderation", callback_data=f"{PREFIX}mod"),
                InlineKeyboardButton("📊 Stats", callback_data=f"{PREFIX}stats"),
            ],
            [InlineKeyboardButton("📢 Broadcast", callback_data=f"{PREFIX}broadcast")],
            [
                InlineKeyboardButton("✅ Developer", callback_data=f"{PREFIX}dev"),
                InlineKeyboardButton("⚙️ Settings", callback_data=f"{PREFIX}settings"),
            ],
            [InlineKeyboardButton("📄 Help", callback_data=f"{PREFIX}help")],
            [InlineKeyboardButton("🚪 Exit", callback_data=f"{PREFIX}exit")],
        ]
    )


def moderation_panel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📝 Text Filter", callback_data=f"{PREFIX}text")],
            [InlineKeyboardButton("🖼 Media Filter", callback_data=f"{PREFIX}media")],
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
