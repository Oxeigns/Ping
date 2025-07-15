from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None

async def connect(uri: str, name: str = "bot") -> AsyncIOMotorDatabase:
    global _client, _db
    _client = AsyncIOMotorClient(uri)
    # Ensure the connection is usable
    await _client.admin.command("ping")
    _db = _client[name]
    return _db


def get_db() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("Database not initialized")
    return _db
