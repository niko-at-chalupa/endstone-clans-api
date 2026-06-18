<div align="center">

# Endstone Clans API

</div>

A plugin that manages clans (or teams, if you will). This is meant to be used in conjunction with one of your own plugins, so using it on its own isn't recommended (this genuinely does not do anything without it).

## Features

> - **Portable SQLite database** /
> You can test this plugin in staging, and bring the `clans.db` file to production. While it's not recommended to modify the database while it's still running, you can do it and most of the time you'll be fine.

> - **User-facing commands that let them manage their own clans** /
> Users may create clans, rename their own clans, whatever. They must stay in only one clan, though.

> - **API that _respects_ your language server** /
> No more blindly throwing methods, `getattr`s, and `setattr`s at an `Any` type like in certain other APIs. As long as you import `get_clans_api` and use that, then your language server gets to have all the information to do things like full autocomplete and typehints.

> - **Event system** /
> You can cancel events, do whatever. You can even use this to do things like replace the invite UI with your own.

> - **Extensive config** /
> The config lets you configure a lot.
>
> Every single piece of front-end facing text translatable through the config.

## Documentation

> [!IMPORTANT]
> Always use this by installing the plugin into your environment, not putting it into the server's `plugins/` directory as a `.whl`. Installing will give you the typehints that you're meant to have.

### Quick Start
```python
from endstone_clans_api import (
    get_clans_api, 
    ClanCreateEvent, 
    clan_event_handler, 
    ClansApi
)
from endstone.plugin import Plugin

class ExamplePlugin(Plugin):
    def on_enable(self):
        # This will get the plugin, and then the plugin's API.
        api: ClansApi | None = get_clans_api(self.server.plugin_manager)

        # Since we're doing everything right, there is little-to-no reason that
        # this should return None.
        assert api, "`get_clans_api` returned `None`"
        self.api: ClansApi = api
        
        # Just like Endstone's register_events, you can make a sperate listener
        # class in a different module to make everything cleaner.
        self.api.register_events(self)

    @clan_event_handler
    def on_clan_create(self, event: ClanCreateEvent):
        # Simple test log so you can see that the plugin's API is funcitonal.
        self.logger.info(f"Event: ClanCreateEvent - Name: {event.clan.display_name}, Creator: {event.creator.name}")
        
        # Let's say that we wanted to ban spaces from clan names. Just handle it
        # here.
        if " " in event.clan.display_name:
            event.cancel()
            event.creator.send_error_message("Clan names cannot have spaces in them!")
```
I think you've noticed by now that this feels really native to Endstone. Feels like we're re-implementing their design, and that's a good thing--Endstone's design is *exceptional*.
