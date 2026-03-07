"""
LANEye - Database Module
=========================
Async SQLite storage with host inventory, history tracking,
and migration support.

Author: SiteQ8 (site@hotmail.com)
License: MIT
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

import aiosqlite

logger = logging.getLogger("laneye.database")


class Database:
    def __init__(self, db_path: str = "laneye.db"):
        self.db_path = db_path

    async def initialize(self):
        """Create tables and run migrations."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS hosts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip TEXT UNIQUE NOT NULL,
                    mac TEXT NOT NULL,
                    vendor TEXT DEFAULT 'Unknown',
                    hostname TEXT,
                    status TEXT DEFAULT 'online',
                    method TEXT DEFAULT 'arp',
                    response_time_ms REAL DEFAULT 0,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                )
            """)

            await db.execute("""
                CREATE TABLE IF NOT EXISTS scan_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_hosts INTEGER DEFAULT 0,
                    online_hosts INTEGER DEFAULT 0,
                    duration_seconds REAL DEFAULT 0,
                    subnet TEXT
                )
            """)

            await db.execute("""
                CREATE TABLE IF NOT EXISTS host_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    details TEXT
                )
            """)

            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_hosts_ip ON hosts(ip)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_hosts_status ON hosts(status)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_events_ip ON host_events(ip)"
            )

            await db.commit()
            logger.info(f"Database initialized at {self.db_path}")

    async def upsert_host(self, host: Dict):
        """Insert or update a host record."""
        async with aiosqlite.connect(self.db_path) as db:
            existing = await db.execute(
                "SELECT ip, status FROM hosts WHERE ip = ?", (host["ip"],)
            )
            row = await existing.fetchone()

            now = datetime.now(timezone.utc).isoformat()

            if row is None:
                await db.execute(
                    """INSERT INTO hosts
                       (ip, mac, vendor, hostname, status, method,
                        response_time_ms, first_seen, last_seen)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        host["ip"], host["mac"], host.get("vendor", "Unknown"),
                        host.get("hostname"), host.get("status", "online"),
                        host.get("method", "arp"),
                        host.get("response_time_ms", 0), now, now,
                    ),
                )
                await db.execute(
                    "INSERT INTO host_events (ip, event_type, details) VALUES (?, ?, ?)",
                    (host["ip"], "discovered", f"MAC={host['mac']} Vendor={host.get('vendor')}"),
                )
            else:
                old_status = row[1]
                new_status = host.get("status", "online")
                await db.execute(
                    """UPDATE hosts SET mac=?, vendor=?, hostname=?, status=?,
                       method=?, response_time_ms=?, last_seen=?
                       WHERE ip=?""",
                    (
                        host["mac"], host.get("vendor", "Unknown"),
                        host.get("hostname"), new_status,
                        host.get("method", "arp"),
                        host.get("response_time_ms", 0), now, host["ip"],
                    ),
                )
                if old_status != new_status:
                    await db.execute(
                        "INSERT INTO host_events (ip, event_type, details) VALUES (?, ?, ?)",
                        (host["ip"], f"status_{new_status}", f"Changed from {old_status}"),
                    )

            await db.commit()

    async def update_host_status(self, ip: str, status: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE hosts SET status=? WHERE ip=?", (status, ip)
            )
            await db.execute(
                "INSERT INTO host_events (ip, event_type) VALUES (?, ?)",
                (ip, f"status_{status}"),
            )
            await db.commit()

    async def get_all_hosts(self) -> List[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM hosts ORDER BY ip")
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    async def get_host(self, ip: str) -> Optional[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM hosts WHERE ip = ?", (ip,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def delete_host(self, ip: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM hosts WHERE ip = ?", (ip,))
            await db.commit()

    async def get_host_events(self, ip: str, limit: int = 50) -> List[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM host_events WHERE ip=? ORDER BY timestamp DESC LIMIT ?",
                (ip, limit),
            )
            return [dict(r) for r in await cursor.fetchall()]

    async def record_scan(self, total: int, online: int, duration: float, subnet: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO scan_history
                   (total_hosts, online_hosts, duration_seconds, subnet)
                   VALUES (?, ?, ?, ?)""",
                (total, online, duration, subnet),
            )
            await db.commit()

    async def get_scan_history(self, limit: int = 100) -> List[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM scan_history ORDER BY scan_time DESC LIMIT ?",
                (limit,),
            )
            return [dict(r) for r in await cursor.fetchall()]
