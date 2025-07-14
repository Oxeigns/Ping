import asyncio
from pyrogram import Client
from pyrogram import idle
from config import Config
from helpers.mongo import connect
from handlers import register_all


async def main():
    db = await connect(Config.MONGO_URI)
    app = Client(
        "bot",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN,
    )
    app.db = db
    register_all(app)
    await app.start()
    print("Bot started")
    await idle()
    await app.stop()


if __name__ == "__main__":
    asyncio.run(main())
