from endstone.plugin import PluginManager
from .main import ClansApiPlugin
from .types import Clan
from .database import Database as ClansDatabase
from .api import ClansApi
from .events import (
    ClanEvent,
    ClanCancellableEvent,
    ClanCreateEvent,
    ClanDeleteEvent,
    ClanJoinEvent,
    ClanLeaveEvent,
    ClanKickEvent,
    ClanRenameEvent,
    ClanInviteEvent,
    clan_event_handler,
)
from typing import cast

def get_clans_api(plugin_manager: PluginManager) -> ClansApi | None:
    """
    Get the ClansApi object the plugin uses. Will return None if an error occours.

    ## Note: Make sure you call this in on_enable or something similar. Internally, what this returns (ClansApiPlugin._api) is unset until the plugin's on_load() method gets called by the PluginManager
    """
    try:
        plugin = cast(ClansApiPlugin, plugin_manager.get_plugin("ClansApiPlugin"))
        # I don't trust how it returns "Plugin." For all I know, this could return
        # Plugin | None, just like get_player.
        if not plugin:
            return None

        return plugin.api
    except Exception:
        return None

__all__ = [
    "ClansApiPlugin",
    "Clan",
    "ClansDatabase",
    "ClansApi",
    "get_clans_api",
    "ClanEvent",
    "ClanCancellableEvent",
    "ClanCreateEvent",
    "ClanDeleteEvent",
    "ClanJoinEvent",
    "ClanLeaveEvent",
    "ClanKickEvent",
    "ClanRenameEvent",
    "ClanInviteEvent",
    "clan_event_handler",
    ]