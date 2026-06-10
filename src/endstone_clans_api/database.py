import sqlite3
from pathlib import Path
from abc import ABC, abstractmethod
from .types import Clan
from .etc import remove_minecraft_formatting
from typing import Optional

class Database(ABC):
    #@abstractmethod
    #def create_clan(self, name: str, owner_xuid: int) -> None:
    #    ...
    # Let's not expose this for now

    @abstractmethod
    def get_clan(self, name: str) -> Clan:
        ...
    
    @abstractmethod
    def get_clan_by_xuid(self, name: str) -> Clan:
        ...

    @abstractmethod
    def get_members_xuids(self, owner_xuid: int) -> set[int]:
        ...

    @abstractmethod
    def get_member_clans(self, member_xuid: int) -> Clan:
        # Only one clan per player should be allowed. Of course, that means
        # they can only own one clan, or be in one clan.
        ...

# The following was assisted by Claude
class _Database:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute("DROP TABLE IF EXISTS clan_members")
            conn.execute("DROP TABLE IF EXISTS clans")
            conn.execute("""
                CREATE TABLE clans (
                    owner_xuid INTEGER PRIMARY KEY,
                    clean_name TEXT UNIQUE NOT NULL,
                    display_name TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE clan_members (
                    owner_xuid INTEGER NOT NULL,
                    member_xuid INTEGER NOT NULL,
                    PRIMARY KEY(owner_xuid, member_xuid),
                    FOREIGN KEY(owner_xuid) REFERENCES clans(owner_xuid) ON DELETE CASCADE
                )
            """)
            conn.commit()

    def create_clan(self, display_name: str, owner_xuid: int) -> None:
        clean_name = remove_minecraft_formatting(display_name).lower()
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO clans (owner_xuid, clean_name, display_name) VALUES (?, ?, ?)",
                (owner_xuid, clean_name, display_name)
            )
            # Add owner as a member
            conn.execute(
                "INSERT INTO clan_members (owner_xuid, member_xuid) VALUES (?, ?)",
                (owner_xuid, owner_xuid)
            )
            conn.commit()

    def get_clan(self, clean_name: str) -> Optional[tuple[int, str, str]]:
        with self._get_connection() as conn:
            return conn.execute(
                "SELECT owner_xuid, clean_name, display_name FROM clans WHERE clean_name = ?",
                (clean_name,)
            ).fetchone()

    def get_clan_by_xuid(self, owner_xuid: int) -> Optional[tuple[int, str, str]]:
        with self._get_connection() as conn:
            return conn.execute(
                "SELECT owner_xuid, clean_name, display_name FROM clans WHERE owner_xuid = ?",
                (owner_xuid,)
            ).fetchone()

    def get_members_xuids(self, owner_xuid: int) -> set[int]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT member_xuid FROM clan_members WHERE owner_xuid = ?",
                (owner_xuid,)
            ).fetchall()
        return {row[0] for row in rows}

    def get_member_clans(self, member_xuid: int) -> list[tuple[int, str, str]]:
        with self._get_connection() as conn:
            return conn.execute("""
                SELECT c.owner_xuid, c.clean_name, c.display_name
                FROM clans c
                JOIN clan_members m ON c.owner_xuid = m.owner_xuid
                WHERE m.member_xuid = ?
            """, (member_xuid,)).fetchall()

    def update_clan(
        self,
        owner_xuid: int,
        display_name: str | None = None
    ) -> None:
        with self._get_connection() as conn:
            if display_name is not None:
                clean_name = remove_minecraft_formatting(display_name).lower()
                conn.execute(
                    "UPDATE clans SET clean_name = ?, display_name = ? WHERE owner_xuid = ?",
                    (clean_name, display_name, owner_xuid)
                )
                conn.commit()

    def delete_clan(self, owner_xuid: int) -> None:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM clans WHERE owner_xuid = ?", (owner_xuid,))
            conn.commit()

    def add_member(self, owner_xuid: int, member_xuid: int) -> None:
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO clan_members (owner_xuid, member_xuid) VALUES (?, ?)",
                (owner_xuid, member_xuid)
            )
            conn.commit()

    def remove_member(self, owner_xuid: int, member_xuid: int) -> None:
        with self._get_connection() as conn:
            conn.execute(
                "DELETE FROM clan_members WHERE owner_xuid = ? AND member_xuid = ?",
                (owner_xuid, member_xuid)
            )
            conn.commit()