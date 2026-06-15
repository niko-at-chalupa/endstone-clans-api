from .types import Clan as Clan
from _typeshed import Incomplete
from abc import ABC
from endstone import Player
from endstone.command import CommandSender
from endstone.event import EventPriority
from typing import Any

class ClanEvent(ABC):
    @property
    def event_name(self) -> str: ...

class ClanCancellableEvent(ClanEvent):
    def __init__(self) -> None: ...
    @property
    def cancelled(self) -> bool: ...
    @cancelled.setter
    def cancelled(self, value: bool): ...
    def cancel(self) -> None: ...

def clan_event_handler(func=None, *, priority: EventPriority = ..., ignore_cancelled: bool = False):
    """
    Decorator to register an event handler.

    The first argument of the decorated method must be a subclass of ClanEvent.

    # Example
    ```python
    @clan_event_handler
    def on_some_event(event: SomeClanEvent):
        ...
    ```
    """

class ClanEventManager:
    def __init__(self, plugin) -> None: ...
    def register_events(self, listener: Any) -> None: ...
    def call_event(self, event: ClanEvent) -> None: ...

class ClanCreateEvent(ClanCancellableEvent):
    clan: Incomplete
    creator: Incomplete
    def __init__(self, clan: Clan, creator: Player) -> None: ...

class ClanDeleteEvent(ClanCancellableEvent):
    clan: Incomplete
    def __init__(self, clan: Clan) -> None: ...

class ClanJoinEvent(ClanCancellableEvent):
    clan: Incomplete
    player: Incomplete
    def __init__(self, clan: Clan, player: Player) -> None: ...

class ClanLeaveEvent(ClanCancellableEvent):
    clan: Incomplete
    player: Incomplete
    def __init__(self, clan: Clan, player: Player) -> None: ...

class ClanKickEvent(ClanCancellableEvent):
    clan: Incomplete
    player: Incomplete
    kicker: Incomplete
    def __init__(self, clan: Clan, player: Player, kicker: CommandSender) -> None: ...

class ClanRenameEvent(ClanCancellableEvent):
    clan: Incomplete
    old_name: Incomplete
    new_name: Incomplete
    def __init__(self, clan: Clan, old_name: str, new_name: str) -> None: ...

class ClanInviteEvent(ClanCancellableEvent):
    clan: Incomplete
    inviter: Incomplete
    invitee: Incomplete
    def __init__(self, clan: Clan, inviter: Player, invitee: Player) -> None: ...
