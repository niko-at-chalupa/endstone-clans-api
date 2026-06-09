from .etc import compute_id, remove_minecraft_formatting
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from endstone import asyncio

if TYPE_CHECKING:
    from .main import ClansApiPlugin

class Clan(ABC):
    @property
    @abstractmethod
    def display_name(self) -> str:
        """
        The formatted display name of the clan.
        
        Use this in frontened, no where else.
        """
        ...

    @property
    @abstractmethod
    def owner_xuid(self) -> int:
        """
        The XUID of the clan owner.
        
        Primary key in the database--immutable (owner transfers? forget that!!)
        """
        ...

    @property
    @abstractmethod
    def clean_name(self) -> str:
        """
        The sanitized, **unique**, and lowered name without Minecraft formatting.
        
        Use internally and as a substitute name in commands.
        """
        ...

class _Clan(Clan):
    _display_name: str
    # Primary key
    _owner_xuid: int
    # Internal name, set as UNIQUE, remove Minecraft formatting, use as a
    # substitute name in commands.
    _clean_name: str

    def __init__(self, plugin: 'ClansApiPlugin', display_name: str, owner_xuid: int):
        self._display_name = display_name
        self._owner_xuid = owner_xuid
        self._plugin = plugin

        self._clean_name = remove_minecraft_formatting(display_name).lower()

    @property
    def display_name(self) -> str:
        return self._display_name

    @property
    def owner_xuid(self) -> int:
        return self._owner_xuid

    @property
    def clean_name(self) -> str:
        return self._clean_name