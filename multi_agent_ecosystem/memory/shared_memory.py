import time
import aiosqlite
from typing import Optional


class SharedMemory:
    def __init__(self, db_path: str = "shared_memory.db"):
        self.db_path = db_path

    async def initialize(self) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    agent TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)
            await db.commit()

    async def store(self, key: str, value: str, agent: str) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO memory (key, value, agent, timestamp) VALUES (?, ?, ?, ?)",
                (key, value, agent, time.time()),
            )
            await db.commit()

    async def retrieve(self, key: str) -> Optional[str]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT value FROM memory WHERE key = ?", (key,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

    async def list_keys(self) -> list[str]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT key FROM memory") as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]

    async def append_history(self, agent: str, role: str, content: str) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO conversation_history (agent, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (agent, role, content, time.time()),
            )
            await db.commit()

    async def get_history(self, agent: str) -> list[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT role, content FROM conversation_history WHERE agent = ? ORDER BY id",
                (agent,),
            ) as cursor:
                rows = await cursor.fetchall()
                return [{"role": row[0], "content": row[1]} for row in rows]

    async def clear_history(self, agent: str) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM conversation_history WHERE agent = ?", (agent,))
            await db.commit()
