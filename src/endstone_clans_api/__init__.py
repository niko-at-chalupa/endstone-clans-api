from endstone.plugin import PluginManager
from .main import ClansApiPlugin
from .types import Clan
from .database import Database as ClansDatabase
from .api import ClansApi
from typing import cast

def get_clans_api(plugin_manager: PluginManager) -> ClansApi | None:
    try:
        plugin = cast(ClansApiPlugin, plugin_manager.get_plugin("ClansApiPlugin"))
        # I don't trust how it returns "Plugin." For all I know, this could return
        # Plugin | None, just like get_player.
        if not plugin:
            return None

        return plugin.api
    except Exception:
        return None

__all__ = ["ClansApiPlugin", "Clan", "ClansDatabase", "ClansApi", "get_clans_api"]