# Minimal script to test MTProto long polling on Render
import asyncio
import os
from pyrogram import Client, idle

async def main():
    async with Client('test', bot_token=os.getenv('BOT_TOKEN'), api_id=int(os.getenv('API_ID')), api_hash=os.getenv('API_HASH')) as app:
        await app.send_message(os.getenv('OWNER_ID'), 'Bot started via MTProto long polling.')
        await idle()

if __name__ == '__main__':
    asyncio.run(main())
