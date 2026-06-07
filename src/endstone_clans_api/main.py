from endstone.plugin import Plugin

class ClansApiPlugin(Plugin):
    api_version = "0.11"

    commands = {
        "clan": {
            "description": "Manage or create a clan",
            "usages": [
                "/clan create <name: str>",
                "/clan modify name <name: str>",
                "/clan modify displayname <displayname: str>",
                "/clan invite <player: player>",
                "/clan kick <player: player>",
                "/clan disband <name: str>",
            ],
            "permissions": ["clans-api.command"],
        }
    }

    permissions = {
        "clans-api.command": {
            "description": "Base permission for all endstone clans API commands",
            "default": "op",
        }
    }

    def on_enable(self):
        self.register_events(self)