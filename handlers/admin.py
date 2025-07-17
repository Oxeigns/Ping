from helpers.compat import Client, Message, filters
from helpers.decorators import require_admin, require_owner
from helpers.mongo import get_db
from helpers.abuse import add_word, remove_word, init_words
from config import Config

db = get_db()


def register(app: Client):
    # Helper: extract int safely
    def parse_seconds(cmd, usage_msg):
        if len(cmd) < 2 or not cmd[1].isdigit():
            return None, usage_msg
        return int(cmd[1]), None

    # --- Timers ---

    @app.on_message(filters.command("set_text_timer") & (filters.group | filters.private))
    @require_admin
    async def set_text(client: Client, message: Message):
        seconds, error = parse_seconds(message.command, "❌ Usage: /set_text_timer <seconds>")
        if error:
            return await message.reply_text(error, quote=True)
        await db.group_settings.update_one(
            {"chat_id": message.chat.id},
            {"$set": {"text_timer": seconds}},
            upsert=True
        )
        await message.reply_text(f"✅ Text messages will be deleted after {seconds}s", quote=True)

    @app.on_message(filters.command("set_media_timer") & (filters.group | filters.private))
    @require_admin
    async def set_media(client: Client, message: Message):
        seconds, error = parse_seconds(message.command, "❌ Usage: /set_media_timer <seconds>")
        if error:
            return await message.reply_text(error, quote=True)
        await db.group_settings.update_one(
            {"chat_id": message.chat.id},
            {"$set": {"media_timer": seconds}},
            upsert=True
        )
        await message.reply_text(f"✅ Media will be deleted after {seconds}s", quote=True)

    # --- Abuse List Management (Global) ---

    @app.on_message(filters.command("addabuse") & (filters.group | filters.private))
    @require_owner
    async def add_abuse(client: Client, message: Message):
        if len(message.command) < 2:
            return await message.reply_text("❌ Usage: /addabuse <word>", quote=True)
        word = message.command[1].lower()
        await add_word(word)
        await message.reply_text(f"✅ Word '{word}' added to global filter.", quote=True)

    @app.on_message(filters.command("removeabuse") & (filters.group | filters.private))
    @require_owner
    async def remove_abuse(client: Client, message: Message):
        if len(message.command) < 2:
            return await message.reply_text("❌ Usage: /removeabuse <word>", quote=True)
        word = message.command[1].lower()
        await remove_word(word)
        await message.reply_text(f"✅ Word '{word}' removed from global filter.", quote=True)

    @app.on_message(filters.command("reloadwords") & filters.group)
    @require_admin
    async def reload_banned_words(client: Client, message: Message):
        try:
            init_words()
            await message.reply_text("✅ Banned words reloaded successfully.", quote=True)
        except Exception as e:
            await message.reply_text(f"❌ Failed to reload: {e}", quote=True)

    # --- Group-Specific Whitelist ---

    @app.on_message(filters.command("whitelist") & filters.group)
    @require_owner
    async def whitelist_word(client: Client, message: Message):
        if len(message.command) < 2:
            return await message.reply_text("❌ Usage: /whitelist <word>", quote=True)
        word = message.command[1].lower()
        await db.group_settings.update_one(
            {"chat_id": message.chat.id},
            {"$addToSet": {"whitelist": word}, "$setOnInsert": {"chat_id": message.chat.id}},
            upsert=True,
        )
        await message.reply_text(f"✅ Word '{word}' whitelisted for this group.", quote=True)

    @app.on_message(filters.command("removewhitelist") & filters.group)
    @require_owner
    async def remove_whitelist_word(client: Client, message: Message):
        if len(message.command) < 2:
            return await message.reply_text("❌ Usage: /removewhitelist <word>", quote=True)
        word = message.command[1].lower()
        await db.group_settings.update_one(
            {"chat_id": message.chat.id},
            {"$pull": {"whitelist": word}},
            upsert=True,
        )
        await message.reply_text(f"✅ Word '{word}' removed from whitelist.", quote=True)

    # --- Toggle Filter ---

    @app.on_message(filters.command("filter") & filters.group)
    @require_admin
    async def toggle_filter(client: Client, message: Message):
        current = await db.group_settings.find_one({"chat_id": message.chat.id}) or {}
        if len(message.command) < 2:
            state = "ON ✅" if current.get("filter_enabled", True) else "OFF ❌"
            return await message.reply_text(f"Current filter state: {state}", quote=True)

        enabled = message.command[1].lower() != "off"
        await db.group_settings.update_one(
            {"chat_id": message.chat.id},
            {"$set": {"filter_enabled": enabled}, "$setOnInsert": {"chat_id": message.chat.id}},
            upsert=True,
        )
        state = "enabled ✅" if enabled else "disabled ❌"
        await message.reply_text(f"🔧 Filter {state}.", quote=True)
