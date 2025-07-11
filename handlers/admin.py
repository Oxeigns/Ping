import logging
import json
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
from telegram.ext import MessageHandler, filters

logger = logging.getLogger(__name__)

from helpers import (
    get_or_create_user,
    is_admin,
    approve_user,
)
from config import Config


def register(app: Application):
    async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != Config.OWNER_ID:
            return
        if not context.args:
            await update.message.reply_text("⚠️ Usage:\n`/broadcast <message>`", quote=True)
            return

        text = " ".join(context.args)
        await update.message.reply_text("📢 Broadcasting your message...")
        sent = 0
        async with app.db.execute("SELECT id FROM users") as cur:
            rows = await cur.fetchall()
        for row in rows:
            try:
                await context.bot.send_message(row[0], text)
                sent += 1
            except Exception:
                continue

        await update.message.reply_text(f"✅ Broadcast sent to `{sent}` chats.")

    async def approve_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.effective_message
        if not await is_admin(message):
            return
        if not message.reply_to_message:
            await message.reply_text("👤 Please reply to a user to approve them.")
            return

        user_id = message.reply_to_message.from_user.id
        await approve_user(app.db, user_id, True)
        await message.reply_text(f"✅ Approved [user](tg://user?id={user_id}).", disable_web_page_preview=True)
        logger.info("Approved user %s via %s", user_id, message.from_user.id)

    async def unapprove_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.effective_message
        if not await is_admin(message):
            return
        if not message.reply_to_message:
            await message.reply_text("👤 Please reply to a user to unapprove them.")
            return

        user_id = message.reply_to_message.from_user.id
        await approve_user(app.db, user_id, False)
        await message.reply_text(f"❌ Unapproved [user](tg://user?id={user_id}).", disable_web_page_preview=True)
        logger.info("Unapproved user %s via %s", user_id, message.from_user.id)

    async def approved_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.effective_message
        if not await is_admin(message):
            return

        async with app.db.execute("SELECT id FROM users WHERE approved=1") as cur:
            rows = await cur.fetchall()

        if not rows:
            await message.reply_text("ℹ️ No users have been approved yet.")
            return

        lines = [f"- [user](tg://user?id={row[0]})" for row in rows]
        await message.reply_text("✅ **Approved Users:**\n" + "\n".join(lines), disable_web_page_preview=True)
        logger.info("Listed approved users for %s", message.from_user.id)

    async def rmwarn_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.effective_message
        if not await is_admin(message):
            return
        if not message.reply_to_message:
            await message.reply_text("👤 Please reply to the user whose warnings you want to clear.")
            return

        user_id = message.reply_to_message.from_user.id
        await get_or_create_user(app.db, user_id)
        await app.db.execute("UPDATE users SET warnings=0 WHERE id=?", (user_id,))
        await app.db.commit()
        await message.reply_text(f"✅ Cleared all warnings for [user](tg://user?id={user_id}).", disable_web_page_preview=True)
        logger.info("Cleared warnings for %s via %s", user_id, message.from_user.id)

    app.add_handler(CommandHandler("broadcast", broadcast_handler))
    app.add_handler(CommandHandler("approve", approve_handler))
    app.add_handler(CommandHandler("unapprove", unapprove_handler))
    app.add_handler(CommandHandler("approved", approved_list))
    app.add_handler(CommandHandler("rmwarn", rmwarn_handler))

    logger.info("✅ Admin handlers registered.")

