from .api import ClansApi as ClansApi
from .database import Database as ClansDatabase
from .events import ClanCancellableEvent as ClanCancellableEvent, ClanCreateEvent as ClanCreateEvent, ClanDeleteEvent as ClanDeleteEvent, ClanEvent as ClanEvent, ClanInviteEvent as ClanInviteEvent, ClanJoinEvent as ClanJoinEvent, ClanKickEvent as ClanKickEvent, ClanLeaveEvent as ClanLeaveEvent, ClanRenameEvent as ClanRenameEvent, clan_event_handler as clan_event_handler
from .main import ClansApiPlugin as ClansApiPlugin
from .types import Clan as Clan
from endstone.plugin import PluginManager

__all__ = ['ClansApiPlugin', 'Clan', 'ClansDatabase', 'ClansApi', 'ClanEvent', 'ClanCancellableEvent', 'ClanCreateEvent', 'ClanDeleteEvent', 'ClanJoinEvent', 'ClanLeaveEvent', 'ClanKickEvent', 'ClanRenameEvent', 'ClanInviteEvent', 'clan_event_handler', 'get_clans_api']

def get_clans_api(plugin_manager: PluginManager) -> ClansApi | None:
    """
    Get the ClansApi object the plugin uses. Will return None if an error occours.

    ## Note: Make sure you call this in on_enable or something similar. Internally, what this returns (ClansApiPlugin._api) is unset until the plugin's on_load() method gets called by the PluginManager
    """
