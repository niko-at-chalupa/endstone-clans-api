from endstone_clans_api.database import Database
from abc import ABC
from typing import TYPE_CHECKING, Callable
from endstone.command import CommandSender, Command

if TYPE_CHECKING:
    from .main import ClansConfig, ClansApiPlugin

class Subcommands(ABC):
    # def a_function(self, sender: CommandSender, command: Command, args: list[str]) -> bool: ...
    # { "a": self.a_function }
    # ^ this is what we're asking for (the dict)
    # This should also accept unbound methods (methods that aren't object.method, but rather method(object)), but
    # we won't be using unbound methods anyways so it doesn't matter
    subcommand_map: dict[str, Callable[[CommandSender, Command, list[str]], bool]]
    plugin: 'ClansApiPlugin'

    @property
    def config(self) -> 'ClansConfig':
        return self.plugin.config

    @property
    def messages(self) -> dict[str, str]:
        return self.config.messages

    @property
    def db(self) -> Database:
        return self.plugin.db

class ClansCommands(Subcommands):
    def help(self, sender: CommandSender, command: Command, args: list[str]):
        help_messages = self.config.help

        sender.send_message(self.plugin.config.messages.get("help_header", ""))
        for subcommand in self.subcommand_map:
            if subcommand in help_messages:
                description = help_messages.get(subcommand)
            else:
                description = "[no description]"
            sender.send_message(f"{subcommand} - {description}")

        return True

    def create(self, sender: CommandSender, command: Command, args: list[str]):
        raise NotImplementedError

    def rename(self, sender: CommandSender, command: Command, args: list[str]):
        raise NotImplementedError

    def invite(self, sender: CommandSender, command: Command, args: list[str]):
        raise NotImplementedError

    def kick(self, sender: CommandSender, command: Command, args: list[str]):
        raise NotImplementedError

    def leave(self, sender: CommandSender, command: Command, args: list[str]):
        raise NotImplementedError

    def __init__(self, plugin: 'ClansApiPlugin'):
        self.plugin = plugin

        self.subcommand_map = {
            "help": self.help,
            "create": self.create,
            "rename": self.rename,
            "invite": self.invite,
            "kick": self.kick,
            "leave": self.leave,
        }