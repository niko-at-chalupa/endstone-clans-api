from .api import ClansApi as ClansApi
from .commands import ClansCommands as ClansCommands
from .database import Database as Database
from _typeshed import Incomplete
from endstone.command import Command, CommandSender
from endstone.plugin import Plugin
from pydantic import BaseModel

class ClansConfig(BaseModel):
    messages: dict[str, str]
    help: dict[str, str]
    config_form: dict[str, str]
    invite_cooldown: int

class ClansApiPlugin(Plugin):
    api_version: str
    commands: Incomplete
    permissions: Incomplete
    def on_load(self) -> None: ...
    clans_commands: Incomplete
    def on_enable(self) -> None: ...
    def on_disable(self) -> None: ...
    @property
    def invite_cooldowns(self) -> dict[tuple[str, str], float]: ...
    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool: ...
    @property
    def config(self) -> ClansConfig: ...
    @property
    def api(self) -> ClansApi | None: ...
    @property
    def db(self) -> Database: ...
