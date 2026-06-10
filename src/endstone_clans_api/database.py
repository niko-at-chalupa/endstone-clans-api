import sqlite3
from pathlib import Path
from abc import ABC, abstractmethod
from .types import Clan
from .etc import remove_minecraft_formatting
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .main import ClansApiPlugin

class Database(ABC):
    @abstractmethod
    def create_clan(self, name: str, owner_xuid: int) -> None:
        ...

    @abstractmethod
    def get_clan(self, name: str) -> Optional[Clan]:
        ...

    @abstractmethod
    def get_clan_by_xuid(self, xuid: int) -> Optional[Clan]:
        ...

    @abstractmethod
    def get_members_xuids(self, owner_xuid: int) -> set[int]:
        ...

    @abstractmethod
    def get_member_clan(self, member_xuid: int) -> Optional[Clan]:
        # Only one clan per player should be allowed. Of course, that means
        # they can only own one clan, or be in one clan.
        ...

# The following was assisted by Claude
class _Database(Database):
    def __init__(self, plugin: 'ClansApiPlugin', db_path: Path) -> None:
        self.plugin = plugin
        self.db_path = db_path
        self._init_db()

    def create_clan(self, name: str, owner_xuid: int) -> None:
        self._create_clan(name, owner_xuid)

    def get_clan(self, name: str) -> Optional[Clan]:
        from .types import _Clan
        clean_name = remove_minecraft_formatting(name).lower()
        row = self._get_clan(clean_name)
        return _Clan._from_db(self.plugin, row) if row else None

    def get_clan_by_xuid(self, xuid: int) -> Optional[Clan]:
        from .types import _Clan
        row = self._get_clan_by_xuid(xuid)
        return _Clan._from_db(self.plugin, row) if row else None

    def get_members_xuids(self, owner_xuid: int) -> set[int]:
        return self._get_members_xuids(owner_xuid)

    def get_member_clan(self, member_xuid: int) -> Optional[Clan]:
        from .types import _Clan
        row = self._get_member_clan(member_xuid)
        return _Clan._from_db(self.plugin, row) if row else None

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS clans (
                    owner_xuid INTEGER PRIMARY KEY,
                    clean_name TEXT UNIQUE NOT NULL,
                    display_name TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS clan_members (
                    owner_xuid INTEGER NOT NULL,
                    member_xuid INTEGER NOT NULL UNIQUE,
                    PRIMARY KEY(owner_xuid, member_xuid),
                    FOREIGN KEY(owner_xuid) REFERENCES clans(owner_xuid) ON DELETE CASCADE
                )
            """)
            conn.commit()

    def _create_clan(self, display_name: str, owner_xuid: int) -> None:
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

    def _get_clan(self, clean_name: str) -> Optional[tuple[int, str, str]]:
        with self._get_connection() as conn:
            return conn.execute(
                "SELECT owner_xuid, clean_name, display_name FROM clans WHERE clean_name = ?",
                (clean_name,)
            ).fetchone()

    def _get_clan_by_xuid(self, owner_xuid: int) -> Optional[tuple[int, str, str]]:
        with self._get_connection() as conn:
            return conn.execute(
                "SELECT owner_xuid, clean_name, display_name FROM clans WHERE owner_xuid = ?",
                (owner_xuid,)
            ).fetchone()

    def _get_members_xuids(self, owner_xuid: int) -> set[int]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT member_xuid FROM clan_members WHERE owner_xuid = ?",
                (owner_xuid,)
            ).fetchall()
        return {row[0] for row in rows}

    def _get_member_clan(self, member_xuid: int) -> Optional[tuple[int, str, str]]:
        with self._get_connection() as conn:
            return conn.execute("""
                SELECT c.owner_xuid, c.clean_name, c.display_name
                FROM clans c
                JOIN clan_members m ON c.owner_xuid = m.owner_xuid
                WHERE m.member_xuid = ?
            """, (member_xuid,)).fetchone()

    def _update_clan(
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

    def _delete_clan(self, owner_xuid: int) -> None:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM clans WHERE owner_xuid = ?", (owner_xuid,))
            conn.commit()

    def _add_member(self, owner_xuid: int, member_xuid: int) -> None:
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO clan_members (owner_xuid, member_xuid) VALUES (?, ?)",
                (owner_xuid, member_xuid)
            )
            conn.commit()

    def _remove_member(self, owner_xuid: int, member_xuid: int) -> None:
        with self._get_connection() as conn:
            conn.execute(
                "DELETE FROM clan_members WHERE owner_xuid = ? AND member_xuid = ?",
                (owner_xuid, member_xuid)
            )
            conn.commit()