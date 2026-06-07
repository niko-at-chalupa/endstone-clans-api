import sqlite3
from pathlib import Path

class Database:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS clans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    display_name TEXT,
                    owner_uuid TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS members (
                    clan_id INTEGER,
                    player_uuid TEXT,
                    role TEXT,
                    FOREIGN KEY(clan_id) REFERENCES clans(id) ON DELETE CASCADE,
                    PRIMARY KEY(clan_id, player_uuid)
                )
            """)
            conn.commit()

    def create_clan(self, name: str, owner_uuid: str):
        with self._get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO clans (name, display_name, owner_uuid) VALUES (?, ?, ?)",
                (name, name, owner_uuid)
            )
            clan_id = cursor.lastrowid
            conn.execute(
                "INSERT INTO members (clan_id, player_uuid, role) VALUES (?, ?, ?)",
                (clan_id, owner_uuid, "owner")
            )
            conn.commit()

    def get_clan(self, name: str):
        with self._get_connection() as conn:
            return conn.execute(
                "SELECT id, name, display_name, owner_uuid FROM clans WHERE name = ?",
                (name,)
            ).fetchone()

    def get_member_clans(self, player_uuid: str):
        with self._get_connection() as conn:
            return conn.execute("""
                SELECT c.id, c.name, c.display_name, c.owner_uuid, m.role
                FROM clans c
                JOIN members m ON c.id = m.clan_id
                WHERE m.player_uuid = ?
            """, (player_uuid,)).fetchall()

    def update_clan(self, clan_id: int, name: str = None, display_name: str = None, owner_uuid: str = None):
        with self._get_connection() as conn:
            if name:
                conn.execute("UPDATE clans SET name = ? WHERE id = ?", (name, clan_id))
            if display_name:
                conn.execute("UPDATE clans SET display_name = ? WHERE id = ?", (display_name, clan_id))
            if owner_uuid:
                conn.execute("UPDATE clans SET owner_uuid = ? WHERE id = ?", (owner_uuid, clan_id))
            conn.commit()

    def delete_clan(self, name: str):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM clans WHERE name = ?", (name,))
            conn.commit()

    def add_member(self, clan_id: int, player_uuid: str, role: str = "member"):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO members (clan_id, player_uuid, role) VALUES (?, ?, ?)",
                (clan_id, player_uuid, role)
            )
            conn.commit()

    def remove_member(self, clan_id: int, player_uuid: str):
        with self._get_connection() as conn:
            conn.execute(
                "DELETE FROM members WHERE clan_id = ? AND player_uuid = ?",
                (clan_id, player_uuid)
            )
            conn.commit()
