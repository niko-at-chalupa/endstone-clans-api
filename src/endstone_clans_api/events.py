from endstone import Player
from endstone.command import CommandSender
from .types import Clan
from abc import ABC
from typing import Callable, Type, Any, get_type_hints
import inspect
from endstone.event import EventPriority

class ClanEvent(ABC):
    @property
    def event_name(self) -> str:
        return self.__class__.__name__

class ClanCancellableEvent(ClanEvent):
    def __init__(self):
        self._cancelled = False

    @property
    def cancelled(self) -> bool:
        return self._cancelled

    @cancelled.setter
    def cancelled(self, value: bool):
        self._cancelled = value

    def cancel(self):
        self._cancelled = True

def clan_event_handler(func=None, *, priority: EventPriority = EventPriority.NORMAL, ignore_cancelled: bool = False):
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
    def decorator(f):
        setattr(f, "_is_clan_event_handler", True)
        setattr(f, "_clan_priority", priority)
        setattr(f, "_clan_ignore_cancelled", ignore_cancelled)
        return f

    if func:
        return decorator(func)

    return decorator

class ClanEventManager:
    def __init__(self, plugin):
        self._plugin = plugin
        self._handlers: dict[Type[ClanEvent], list[Callable[[Any], Any]]] = {}

    def register_events(self, listener: Any) -> None:
        for attr_name in dir(listener):
            attr = getattr(listener, attr_name)
            if not callable(attr) or not getattr(attr, "_is_clan_event_handler", False):
                continue

            hints = get_type_hints(attr)
            hints.pop("return", None)
            
            event_type = next(iter(hints.values()), None)

            if not inspect.isclass(event_type) or not issubclass(event_type, ClanEvent):
                self._plugin.logger.error(f"Failed to register clan event handler {attr_name}: No ClanEvent type hint found.")
                continue

            if event_type not in self._handlers:
                self._handlers[event_type] = []
            
            self._handlers[event_type].append(attr)
            self._handlers[event_type].sort(key=lambda x: getattr(x, "_clan_priority").value)

    def call_event(self, event: ClanEvent) -> None:
        for registered_type, handlers in self._handlers.items():
            if isinstance(event, registered_type):
                handler: Callable[[Any], Any]
                for handler in handlers:
                    if isinstance(event, ClanCancellableEvent) and event.cancelled and not getattr(handler, "_clan_ignore_cancelled"):
                        continue
                    try:
                        handler(event)
                    except Exception as e:
                        handler_name = getattr(handler, "__name__", str(handler))
                        self._plugin.logger.error(f"Error while calling clan event handler {handler_name}: {e}")
                        import traceback
                        self._plugin.logger.error(traceback.format_exc())

class ClanCreateEvent(ClanCancellableEvent):
    def __init__(self, clan: Clan, creator: Player):
        super().__init__()
        self.clan = clan
        self.creator = creator

class ClanDeleteEvent(ClanCancellableEvent):
    def __init__(self, clan: Clan):
        super().__init__()
        self.clan = clan

class ClanJoinEvent(ClanCancellableEvent):
    def __init__(self, clan: Clan, player: Player):
        super().__init__()
        self.clan = clan
        self.player = player

class ClanLeaveEvent(ClanCancellableEvent):
    def __init__(self, clan: Clan, player: Player):
        super().__init__()
        self.clan = clan
        self.player = player

class ClanKickEvent(ClanCancellableEvent):
    def __init__(self, clan: Clan, player: Player, kicker: CommandSender):
        super().__init__()
        self.clan = clan
        self.player = player
        self.kicker = kicker

class ClanRenameEvent(ClanCancellableEvent):
    def __init__(self, clan: Clan, old_name: str, new_name: str):
        super().__init__()
        self.clan = clan
        self.old_name = old_name
        self.new_name = new_name

class ClanInviteEvent(ClanCancellableEvent):
    def __init__(self, clan: Clan, inviter: Player, invitee: Player):
        super().__init__()
        self.clan = clan
        self.inviter = inviter
        self.invitee = invitee
