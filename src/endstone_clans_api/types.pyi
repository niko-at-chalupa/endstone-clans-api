import abc
from .etc import compute_id as compute_id, remove_minecraft_formatting as remove_minecraft_formatting
from .main import ClansApiPlugin as ClansApiPlugin
from abc import ABC, abstractmethod
from endstone import asyncio as asyncio

class Clan(ABC, metaclass=abc.ABCMeta):
    @property
    @abstractmethod
    def display_name(self) -> str:
        """
        The formatted display name of the clan.
        
        Use this in frontened, no where else.
        """
    @property
    @abstractmethod
    def owner_xuid(self) -> int:
        """
        The XUID of the clan owner.
        
        Primary key in the database--immutable (owner transfers? forget that!!)
        """
    @property
    @abstractmethod
    def clean_name(self) -> str:
        """
        The sanitized, **unique**, and lowered name without Minecraft formatting.
        
        Use internally and as a substitute name in commands.
        """
    @property
    @abstractmethod
    def members_xuids(self) -> set[int]:
        """
        XUIDs of every player in this clan, including the owner.
        """

class _Clan(Clan):
    def __init__(self, plugin: ClansApiPlugin, display_name: str, owner_xuid: int) -> None: ...
    @property
    def display_name(self) -> str: ...
    @property
    def owner_xuid(self) -> int: ...
    @property
    def clean_name(self) -> str: ...
    @property
    def members_xuids(self) -> set[int]: ...
