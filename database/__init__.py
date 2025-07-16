from datetime import datetime
from typing import Any, Dict
from motor.motor_asyncio import AsyncIOMotorDatabase

__all__ = [
    "init_db",
    "get_or_create_user",
    "add_warning",
    "approve_user",
    "is_approved",
    "add_log",
    "upsert_group",
    "remove_group",
]


async def init_db(db: AsyncIOMotorDatabase) -> None:
    """Create indexes used by the bot."""
    await db.users.create_index("_id", unique=True)
    await db.logs.create_index("user_id")
    await db.groups.create_index("_id", unique=True)


async def get_or_create_user(db: AsyncIOMotorDatabase, user_id: int) -> Dict[str, Any]:
    """Fetch a user document or create it if missing."""
    user = await db.users.find_one({"_id": user_id})
    if user:
        return user
    user = {
        "_id": user_id,
        "global_toxicity": 0.0,
        "warnings": 0,
        "approved": False,
        "mutes": 0,
        "last_violation": None,
    }
    await db.users.insert_one(user)
    return user


async def add_warning(db: AsyncIOMotorDatabase, user_id: int, score: float) -> Dict[str, Any]:
    """Increment warning counters and return the updated user."""
    user = await get_or_create_user(db, user_id)
    new_global = user["global_toxicity"] + score
    new_warn = user["warnings"] + 1
    last_violation = datetime.utcnow().isoformat()
    await db.users.update_one(
        {"_id": user_id},
        {"$set": {"global_toxicity": new_global, "warnings": new_warn, "last_violation": last_violation}},
    )
    user.update(global_toxicity=new_global, warnings=new_warn, last_violation=last_violation)
    return user


async def approve_user(db: AsyncIOMotorDatabase, user_id: int, value: bool) -> Dict[str, Any]:
    """Mark a user as approved or not."""
    await get_or_create_user(db, user_id)
    await db.users.update_one({"_id": user_id}, {"$set": {"approved": bool(value)}})
    return await get_or_create_user(db, user_id)


async def is_approved(db: AsyncIOMotorDatabase, user_id: int) -> bool:
    """Check whether a user has been approved."""
    doc = await db.users.find_one({"_id": user_id}, {"approved": 1})
    return bool(doc and doc.get("approved"))


async def add_log(db: AsyncIOMotorDatabase, user_id: int, chat_id: int, reason: str, score: float) -> None:
    """Record a moderation log entry."""
    await db.logs.insert_one(
        {
            "user_id": user_id,
            "chat_id": chat_id,
            "reason": reason,
            "score": score,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


async def upsert_group(
    db: AsyncIOMotorDatabase,
    chat_id: int,
    title: str,
    username: str | None = None,
    members: int = 0,
    link: str | None = None,
) -> None:
    """Insert or update a Telegram group entry."""
    await db.groups.update_one(
        {"_id": chat_id},
        {"$set": {"title": title, "username": username, "members": members, "link": link}},
        upsert=True,
    )


async def remove_group(db: AsyncIOMotorDatabase, chat_id: int) -> None:
    """Remove a group from the database."""
    await db.groups.delete_one({"_id": chat_id})
