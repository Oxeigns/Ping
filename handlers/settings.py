from helpers.compat import Client, Message, CallbackQuery, filters
from helpers.panels import settings_panel
from helpers.formatting import safe_edit


def register(app: Client):
    @app.on_message(filters.command("settings") & (filters.group | filters.private))
    async def open_settings(client: Client, message: Message):
        resp = await message.reply("⚙️ Settings", quote=True)
        await safe_edit(resp, "**Settings**", reply_markup=settings_panel())

    @app.on_callback_query(filters.regex("^settings:"))
    async def settings_cb(_: Client, query: CallbackQuery):
        await safe_edit(query.message, "**Settings**", reply_markup=settings_panel())
        await query.answer()
