"""Database Module"""
import aiosqlite

class Database:
    def __init__(self, db_path="laneye.db"):
        self.db_path = db_path

    async def initialize(self):
        """Initialize database"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS hosts (
                    id INTEGER PRIMARY KEY,
                    ip TEXT UNIQUE,
                    mac TEXT,
                    status TEXT,
                    last_seen TIMESTAMP
                )
            """)
            await db.commit()

    async def get_all_hosts(self):
        """Get all hosts"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT * FROM hosts")
            rows = await cursor.fetchall()
            return rows
