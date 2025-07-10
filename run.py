import asyncio
from pyrogram import Client
from config import Config
from handlers import register_all

app = Client(
    "my_bot",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
)

async def main():
    await app.start()
    register_all(app)
    print("✅ Bot Started")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
