import aiosqlite
from datetime import datetime
from typing import Dict, Any


async def init_db(db: aiosqlite.Connection):
    """
    Initialize database tables if they don't exist.
    """
    await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            global_toxicity REAL DEFAULT 0,
            warnings INTEGER DEFAULT 0,
            approved INTEGER DEFAULT 0,
            mutes INTEGER DEFAULT 0,
            last_violation TEXT
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            chat_id INTEGER,
            reason TEXT,
            score REAL,
            timestamp TEXT
        )
    """)
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY,
            title TEXT,
            username TEXT,
            members INTEGER DEFAULT 0,
            link TEXT
        )
    """
    )
    await db.commit()


async def get_or_create_user(db: aiosqlite.Connection, user_id: int) -> Dict[str, Any]:
    """
    Fetch a user by ID, or create a new record if they don't exist.
    """
    async with db.execute("SELECT * FROM users WHERE id = ?", (user_id,)) as cur:
        row = await cur.fetchone()
        columns = [c[0] for c in cur.description]

    if row:
        return dict(zip(columns, row))

    await db.execute("""
        INSERT INTO users (id, global_toxicity, warnings, approved, mutes, last_violation)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, 0.0, 0, 0, 0, None))
    await db.commit()

    return {
        "id": user_id,
        "global_toxicity": 0.0,
        "warnings": 0,
        "approved": 0,
        "mutes": 0,
        "last_violation": None,
    }


async def add_warning(db: aiosqlite.Connection, user_id: int, score: float) -> Dict[str, Any]:
    """
    Increment user's warning count and update toxicity score.
    """
    user = await get_or_create_user(db, user_id)
    user["global_toxicity"] += score
    user["warnings"] += 1
    user["last_violation"] = datetime.utcnow().isoformat()

    await db.execute("""
        UPDATE users
        SET global_toxicity = ?, warnings = ?, last_violation = ?
        WHERE id = ?
    """, (user["global_toxicity"], user["warnings"], user["last_violation"], user_id))
    await db.commit()

    return user


async def approve_user(db: aiosqlite.Connection, user_id: int, value: bool) -> Dict[str, Any]:
    """
    Approve or unapprove a user.
    """
    await get_or_create_user(db, user_id)
    await db.execute("""
        UPDATE users SET approved = ? WHERE id = ?
    """, (int(value), user_id))
    await db.commit()
    return await get_or_create_user(db, user_id)


async def is_approved(db: aiosqlite.Connection, user_id: int) -> bool:
    """Return True if the user is approved."""
    async with db.execute("SELECT approved FROM users WHERE id=?", (user_id,)) as cur:
        row = await cur.fetchone()
    if row is None:
        return False
    return bool(row[0])


async def add_log(db: aiosqlite.Connection, user_id: int, chat_id: int, reason: str, score: float):
    """
    Store a violation log for a user.
    """
    await db.execute("""
        INSERT INTO logs (user_id, chat_id, reason, score, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, chat_id, reason, score, datetime.utcnow().isoformat()))
    await db.commit()


async def upsert_group(
    db: aiosqlite.Connection,
    chat_id: int,
    title: str,
    username: str | None = None,
    members: int = 0,
    link: str | None = None,
) -> None:
    """Insert or update a group entry."""
    await db.execute(
        """
        INSERT INTO groups (id, title, username, members, link)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            title=excluded.title,
            username=excluded.username,
            members=excluded.members,
            link=excluded.link
        """,
        (chat_id, title, username, members, link),
    )
    await db.commit()


async def remove_group(db: aiosqlite.Connection, chat_id: int) -> None:
    """Remove a group from the database."""
    await db.execute("DELETE FROM groups WHERE id=?", (chat_id,))
    await db.commit()
