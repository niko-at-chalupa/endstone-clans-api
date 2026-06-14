from endstone.plugin import Plugin
from endstone_clans_api import (
    get_clans_api,
    ClanCreateEvent,
    ClanDeleteEvent,
    ClanJoinEvent,
    ClanLeaveEvent,
    ClanKickEvent,
    ClanRenameEvent,
    ClanInviteEvent,
    clan_event_handler,
)

class TestPlugin(Plugin):
    def on_enable(self):
        api = get_clans_api(self.server.plugin_manager)
        if api:
            self.logger.info("Clans API found! Registering test events...")
            api.register_events(self)
        else:
            self.logger.error("Clans API NOT found!")

    @clan_event_handler
    def on_clan_create(self, event: ClanCreateEvent):
        self.logger.info(f"Event: ClanCreateEvent - Name: {event.clan.display_name}, Creator: {event.creator.name}")

    @clan_event_handler
    def on_clan_delete(self, event: ClanDeleteEvent):
        self.logger.info(f"Event: ClanDeleteEvent - Name: {event.clan.display_name}")

    @clan_event_handler
    def on_clan_join(self, event: ClanJoinEvent):
        self.logger.info(f"Event: ClanJoinEvent - Clan: {event.clan.display_name}, Player: {event.player.name}")

    @clan_event_handler
    def on_clan_leave(self, event: ClanLeaveEvent):
        self.logger.info(f"Event: ClanLeaveEvent - Clan: {event.clan.display_name}, Player: {event.player.name}")

    @clan_event_handler
    def on_clan_kick(self, event: ClanKickEvent):
        self.logger.info(f"Event: ClanKickEvent - Clan: {event.clan.display_name}, Player: {event.player.name}, Kicker: {event.kicker.name}")

    @clan_event_handler
    def on_clan_rename(self, event: ClanRenameEvent):
        self.logger.info(f"Event: ClanRenameEvent - Old: {event.old_name}, New: {event.new_name}")

    @clan_event_handler
    def on_clan_invite(self, event: ClanInviteEvent):
        self.logger.info(f"Event: ClanInviteEvent - Clan: {event.clan.display_name}, Inviter: {event.inviter.name}, Invitee: {event.invitee.name}")
