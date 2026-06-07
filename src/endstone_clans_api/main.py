from endstone.plugin import Plugin

class ClansApiPlugin(Plugin):
    api_version = "0.11"

    def on_enable(self):
        self.register_events(self)