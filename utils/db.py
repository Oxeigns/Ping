from datetime import datetime
from typing import Dict, Any


async def get_or_create_user(db, user_id: int) -> Dict[str, Any]:
    user = await db.users.find_one({"_id": user_id})
    if not user:
        user = {
            "_id": user_id,
            "global_toxicity_score": 0.0,
            "warnings": 0,
            "approved": False,
            "mutes": 0,
            "last_violation": None,
        }
        await db.users.insert_one(user)
    return user


async def add_warning(db, user_id: int, score: float) -> Dict[str, Any]:
    user = await get_or_create_user(db, user_id)
    user["global_toxicity_score"] += score
    user["warnings"] += 1
    user["last_violation"] = datetime.utcnow()
    await db.users.replace_one({"_id": user_id}, user, upsert=True)
    return user


async def approve_user(db, user_id: int, value: bool) -> Dict[str, Any]:
    user = await get_or_create_user(db, user_id)
    user["approved"] = value
    await db.users.replace_one({"_id": user_id}, user, upsert=True)
    return user


async def update_violation(db, user_id: int, score_delta: float, action: str) -> Dict[str, Any]:
    user = await get_or_create_user(db, user_id)
    user["global_toxicity_score"] += score_delta
    user["last_violation"] = action
    await db.users.replace_one({"_id": user_id}, user, upsert=True)
    return user
