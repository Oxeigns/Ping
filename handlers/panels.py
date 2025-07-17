from datetime import datetime
import logging
from helpers.compat import Client, CallbackQuery, Message, ChatMemberStatus, filters
from config import Config
from helpers import safe_edit, send_message_safe
from helpers.panels import (
    admin_panel,
    main_panel,
    moderation_panel,
)

logger = logging.getLogger(__name__)

COMMANDS = {
    "/approve": "Approve a user",
    "/rmwarn": "Remove a warning",
    "/broadcast": "Broadcast a message",
    "/status": "Check group moderation status",
    "/menu": "Open control panel",
    "/off_text_delete": "Toggle text filter",
    "/off_media_delete": "Toggle media filter",
}


def command_list() -> str:
    return "\n".join(f"{cmd} – {desc}" for cmd, desc in COMMANDS.items())


async def send_welcome(message: Message, bot_name: str) -> None:
    user = message.from_user
    name = user.first_name if user else "there"
    text = (
        f"👋 Hello {name}!\n"
        f"I’m <b>{bot_name}</b>, your AI-powered group assistant.\n\n"
        f"<b>Popular Commands:</b>\n{command_list()}"
    )
    if Config.PANEL_IMAGE:
        await message.reply_photo(
            Config.PANEL_IMAGE,
            caption=text,
            reply_markup=main_panel(),
        )
    else:
        await send_message_safe(message, text, reply_markup=main_panel())


def register(app: Client):
    @app.on_message(filters.command(["start", "menu", "help"]) & (filters.group | filters.private))
    async def start_handler(client: Client, message: Message):
        me = await client.get_me()
        await send_welcome(message, me.first_name)

        # Log private user starts
        if message.chat.type == "private" and Config.LOG_CHANNEL:
            user = message.from_user
            if user:
                log_text = (
                    f"#START\n"
                    f"👤 ID: <code>{user.id}</code>\n"
                    f"🧑 Name: {user.first_name}\n"
                    f"🔗 Username: @{user.username or 'N/A'}\n"
                    f"🕒 Time: {datetime.utcnow().isoformat()}"
                )
                try:
                    await client.send_message(Config.LOG_CHANNEL, log_text, parse_mode="HTML")
                except Exception as exc:
                    logger.warning("Failed to send start log: %s", exc)

    @app.on_callback_query(filters.regex("^panel:"))
    async def callbacks(client: Client, query: CallbackQuery):
        data = query.data
        chat_id = query.message.chat.id
        user_first = query.from_user.first_name

        async def is_admin() -> bool:
            if query.from_user.id == Config.OWNER_ID:
                return True
            try:
                member = await client.get_chat_member(chat_id, query.from_user.id)
                return member.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}
            except Exception:
                return False

        try:
            if data == "panel:mod":
                await safe_edit(
                    query.message,
                    "**Abuse Filter**\nDetects and deletes abusive messages. Warns the user automatically.",
                    reply_markup=moderation_panel(chat_id),
                )
            elif data == "panel:stats":
                await client.send_message(chat_id, "/status")
            elif data == "panel:broadcast":
                if not await is_admin():
                    await query.answer("❌ You are not allowed to broadcast.", show_alert=True)
                    return
                await client.send_message(chat_id, "/broadcast")
            elif data == "panel:admin":
                await safe_edit(query.message, "**Admin Tools**", reply_markup=admin_panel())
            elif data == "panel:dev":
                await safe_edit(
                    query.message,
                    f"<b>Developer:</b> <a href='{Config.DEV_URL}'>{Config.DEV_NAME}</a>",
                    reply_markup=main_panel(),
                )
            elif data == "panel:text":
                await client.send_message(chat_id, "/off_text_delete")
            elif data == "panel:media":
                await client.send_message(chat_id, "/off_media_delete")
            elif data == "panel:whitelist":
                await client.send_message(
                    chat_id,
                    "Usage: /whitelist <word> — only owners can whitelist abusive words.",
                )
            elif data == "panel:sendapprove":
                if not await is_admin():
                    await query.answer("❌ You are not allowed to approve users.", show_alert=True)
                    return
                await client.send_message(chat_id, "/approve @username")
            elif data == "panel:rmwarn":
                await client.send_message(chat_id, "/rmwarn <user_id>")
            elif data == "panel:unban":
                await client.send_message(chat_id, "/unban <user_id>")
            elif data == "panel:exit":
                await safe_edit(query.message, "👋 Panel closed.", reply_markup=None)
            elif data == "panel:main":
                me = await client.get_me()
                await safe_edit(
                    query.message,
                    f"👋 Hello {user_first}! I’m {me.first_name}, your AI-powered group assistant.",
                    reply_markup=main_panel(),
                )
            await query.answer()
        except Exception as e:
            logger.error("Callback failed: %s", e)
            await query.answer("Something went wrong.", show_alert=True)
