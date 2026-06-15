from .database import Database as Database
from .events import ClanEvent as ClanEvent, ClanEventManager as ClanEventManager
from .main import ClansApiPlugin as ClansApiPlugin
from .types import Clan as Clan
from _typeshed import Incomplete
from endstone.plugin import PluginManager as PluginManager
from typing import Any

class ClansApi:
    plugin: Incomplete
    def __init__(self, clans_api_plugin: ClansApiPlugin) -> None: ...
    @property
    def db(self) -> Database: ...
    def register_events(self, listener: Any) -> None:
        """Registers clan event handlers."""
    def call_event(self, event: ClanEvent) -> None:
        """Calls clan event handlers."""
