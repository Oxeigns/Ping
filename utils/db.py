from typing import Any, Dict, List


async def get_user(db, user_id: int) -> Dict[str, Any]:
    user = await db.users.find_one({"_id": user_id})
    if not user:
        user = {"_id": user_id, "score": 0, "warnings": {}, "approved_in": []}
        await db.users.insert_one(user)
    return user


async def add_warning(db, chat_id: int, user_id: int, score_delta: int = 1) -> int:
    user = await get_user(db, user_id)
    warnings = user.get("warnings", {})
    key = str(chat_id)
    warnings[key] = warnings.get(key, 0) + 1
    user["warnings"] = warnings
    user["score"] += score_delta
    await db.users.update_one({"_id": user_id}, {"$set": user})
    return warnings[key]


async def reset_warnings(db, chat_id: int, user_id: int) -> None:
    user = await get_user(db, user_id)
    warnings = user.get("warnings", {})
    warnings[str(chat_id)] = 0
    await db.users.update_one({"_id": user_id}, {"$set": {"warnings": warnings}})


async def set_approved(db, chat_id: int, user_id: int, value: bool) -> None:
    user = await get_user(db, user_id)
    approved = set(user.get("approved_in", []))
    if value:
        approved.add(int(chat_id))
    else:
        approved.discard(int(chat_id))
    await db.users.update_one({"_id": user_id}, {"$set": {"approved_in": list(approved)}})


async def list_approved(db, chat_id: int) -> List[int]:
    cursor = db.users.find({"approved_in": {"$in": [int(chat_id)]}})
    return [doc["_id"] async for doc in cursor]


async def add_group(db, chat_id: int) -> None:
    await db.groups.update_one({"_id": chat_id}, {"$set": {"_id": chat_id}}, upsert=True)


async def get_groups(db) -> List[int]:
    cursor = db.groups.find()
    return [doc["_id"] async for doc in cursor]
