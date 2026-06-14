from .types import Clan
from .database import Database
from .events import ClanEventManager, ClanEvent
from endstone.plugin import PluginManager
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
   from .main import ClansApiPlugin 

class ClansApi:
    # I _should_ go for a service, but it's confusing, and services do
    # not provide type hints for the end user's langage server so it's
    # better if I provide it as a function somewhere.

    def __init__(self, clans_api_plugin: 'ClansApiPlugin'):
        self.plugin = clans_api_plugin
        self._event_manager = ClanEventManager(clans_api_plugin)

    @property
    def db(self) -> Database:
        return self.plugin.db

    def register_events(self, listener: Any) -> None:
        """Registers clan event handlers."""
        self._event_manager.register_events(listener)

    def call_event(self, event: ClanEvent) -> None:
        """Calls clan event handlers."""
        self._event_manager.call_event(event)
