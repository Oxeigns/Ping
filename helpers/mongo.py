"""MongoDB helpers with optional Motor dependency."""

from typing import Optional

try:  # pragma: no cover - optional dependency
    from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
    MOTOR_AVAILABLE = True
except Exception:  # pragma: no cover - motor missing
    MOTOR_AVAILABLE = False

    class AsyncIOMotorClient:  # pragma: no cover - placeholder for type hints
        pass

    class AsyncIOMotorDatabase:  # pragma: no cover - placeholder
        pass

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None

async def connect(uri: str, name: str = "bot") -> AsyncIOMotorDatabase:
    """Connect to MongoDB if ``motor`` is installed."""
    if not MOTOR_AVAILABLE:  # pragma: no cover - used only in production
        raise RuntimeError("motor package required for database access")
    global _client, _db
    _client = AsyncIOMotorClient(uri)
    await _client.admin.command("ping")
    _db = _client[name]
    return _db


def get_db() -> AsyncIOMotorDatabase:
    """Return the connected database or raise if ``connect`` wasn't called."""
    if _db is None:
        raise RuntimeError("Database not initialized")
    return _db
