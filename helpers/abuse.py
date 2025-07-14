from .mongo import get_db

async def add_word(word: str) -> None:
    db = get_db()
    await db.abuse_words.update_one({"word": word}, {"$set": {"word": word}}, upsert=True)

async def remove_word(word: str) -> None:
    db = get_db()
    await db.abuse_words.delete_one({"word": word})

async def get_words() -> list[str]:
    db = get_db()
    cursor = db.abuse_words.find({}, {"_id": 0, "word": 1})
    return [doc["word"] async for doc in cursor]

async def contains_abuse(text: str) -> bool:
    words = await get_words()
    text = text.lower()
    return any(w.lower() in text for w in words)
