from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

PREFIX = "panel:"


def main_panel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🔧 Moderation", callback_data=f"{PREFIX}mod")],
            [InlineKeyboardButton("⚙️ Settings", callback_data=f"{PREFIX}settings")],
            [InlineKeyboardButton("👮 Admin Tools", callback_data=f"{PREFIX}admin")],
            [InlineKeyboardButton("📊 Status", callback_data=f"{PREFIX}status")],
            [InlineKeyboardButton("ℹ️ Help", callback_data=f"{PREFIX}help")],
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
