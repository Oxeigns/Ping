from datetime import datetime
from typing import Dict, Any


async def get_user(db, user_id: int) -> Dict[str, Any]:
    user = await db.users.find_one({"_id": user_id})
    if not user:
        user = {"_id": user_id, "score": 0, "violations": 0, "last_action": None}
        await db.users.insert_one(user)
    return user


async def update_violation(db, user_id: int, score_delta: int, action: str):
    user = await get_user(db, user_id)
    user["score"] += score_delta
    user["violations"] += 1
    user["last_action"] = action
    await db.users.replace_one({"_id": user_id}, user, upsert=True)
    return user
