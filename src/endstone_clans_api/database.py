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
            conn.execute("DROP TABLE IF EXISTS members")
            conn.execute("DROP TABLE IF EXISTS clans")
            conn.execute("""
                CREATE TABLE clans (
                    owner_xuid INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    display_name TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE members (
                    owner_xuid INTEGER,
                    player_uuid TEXT,
                    role TEXT,
                    FOREIGN KEY(owner_xuid) REFERENCES clans(owner_xuid) ON DELETE CASCADE,
                    PRIMARY KEY(owner_xuid, player_uuid)
                )
            """)
            conn.commit()

    def create_clan(self, name: str, owner_xuid: int):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO clans (name, display_name, owner_xuid) VALUES (?, ?, ?)",
                (name, name, owner_xuid)
            )
            conn.execute(
                "INSERT INTO members (owner_xuid, player_uuid, role) VALUES (?, ?, ?)",
                (owner_xuid, str(owner_xuid), "owner")
            )
            conn.commit()

    def get_clan(self, name: str):
        with self._get_connection() as conn:
            return conn.execute(
                "SELECT owner_xuid, name, display_name FROM clans WHERE name = ?",
                (name,)
            ).fetchone()

    def get_member_clans(self, player_uuid: str):
        with self._get_connection() as conn:
            return conn.execute("""
                SELECT c.owner_xuid, c.name, c.display_name, m.role
                FROM clans c
                JOIN members m ON c.owner_xuid = m.owner_xuid
                WHERE m.player_uuid = ?
            """, (player_uuid,)).fetchall()

    def update_clan(self, owner_xuid: int, name: str | None = None, display_name: str | None = None):
        with self._get_connection() as conn:
            if name:
                conn.execute("UPDATE clans SET name = ? WHERE owner_xuid = ?", (name, owner_xuid))
            if display_name:
                conn.execute("UPDATE clans SET display_name = ? WHERE owner_xuid = ?", (display_name, owner_xuid))
            conn.commit()

    def delete_clan(self, name: str):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM clans WHERE name = ?", (name,))
            conn.commit()

    def add_member(self, owner_xuid: int, player_uuid: str, role: str = "member"):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO members (owner_xuid, player_uuid, role) VALUES (?, ?, ?)",
                (owner_xuid, player_uuid, role)
            )
            conn.commit()

    def remove_member(self, owner_xuid: int, player_uuid: str):
        with self._get_connection() as conn:
            conn.execute(
                "DELETE FROM members WHERE owner_xuid = ? AND player_uuid = ?",
                (owner_xuid, player_uuid)
            )
            conn.commit()
