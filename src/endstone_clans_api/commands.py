from endstone import Logger
from endstone.scheduler import Scheduler
from endstone.form import MessageForm
from endstone_clans_api.database import Database
from abc import ABC
from typing import TYPE_CHECKING, Callable, TypeVar
from endstone.command import CommandSender, Command
from endstone.asyncio import get_loop, submit
from endstone import Player
from typing import Awaitable
import concurrent.futures
import time

if TYPE_CHECKING:
    from .main import ClansConfig, ClansApiPlugin

_T = TypeVar("_T")

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

    @property
    def scheduler(self) -> Scheduler:
        return self.plugin.server.scheduler

    @property
    def logger(self) -> Logger:
        return self.plugin.logger

    def _handle_future_result(self, future) -> None:
        try:
            future.result()
        except Exception as e:
            self.logger.error(str(e))

    def _submit_and_handle_future_result(self, coro: Awaitable[_T]) -> concurrent.futures.Future[_T]:
        future = submit(coro)
        future.add_done_callback(self._handle_future_result)
        return future

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
        if not isinstance(sender, Player):
            sender.send_error_message(self.messages.get("not_a_player", "Only players can use this command."))
            return True

        if len(args) == 0:
            sender.send_error_message(self.messages.get("usage_create", "Usage: /clan create <name: str>"))
            return True

        clan_name = " ".join(args)

        async def create_task():
            try:
                xuid = int(sender.xuid)
                member_clan = self.db.get_member_clan(xuid)
                if member_clan:
                    self.scheduler.run_task(self.plugin, lambda: sender.send_error_message(self.messages.get("already_in_clan", "already in clan")))
                    return

                existing_clan = self.db.get_clan(clan_name)
                if existing_clan:
                    self.scheduler.run_task(self.plugin, lambda: sender.send_error_message(self.messages.get("clan_name_taken", "clan name taken")))
                    return

                self.db.create_clan(clan_name, xuid)
                
                msg = self.messages.get("clan_created", "clan created")
                msg = msg.replace("[clan_name]", clan_name)
                self.scheduler.run_task(self.plugin, lambda: sender.send_message(msg))
            except Exception as e:
                # What is the point
                raise e

        self._submit_and_handle_future_result(create_task())
        return True

    def rename(self, sender: CommandSender, command: Command, args: list[str]):
        if not isinstance(sender, Player):
            sender.send_error_message(self.messages.get("not_a_player", "Only players can use this command."))
            return True

        if len(args) == 0:
            sender.send_error_message(self.messages.get("usage_create", "Usage: /clan rename <name: str>"))
            return True

        player = sender

        async def rename_task():
            clan = self.db.get_clan_by_xuid(int(player.xuid))
            
            if not clan:
                self.scheduler.run_task(self.plugin, lambda: sender.send_error_message(self.messages.get("not_in_a_clan", "not in a clan")))
                return

            if clan.owner_xuid != player.xuid:
                self.scheduler.run_task(self.plugin, lambda: sender.send_error_message(self.messages.get("not_the_owner", "not the owner")))
                return

            try:
                self.db.rename_clan(clan.owner_xuid, args[0])
            except RuntimeError:
                self.scheduler.run_task(self.plugin, lambda: sender.send_error_message(self.messages.get("clan_name_already_taken", "clan name already taken")))
                return

        self._submit_and_handle_future_result(rename_task())

    def invite(self, sender: CommandSender, command: Command, args: list[str]):
        if not isinstance(sender, Player):
            sender.send_error_message(self.messages.get("not_a_player", "Only players can use this command."))
            return True

        if len(args) == 0:
            sender.send_error_message(self.messages.get("usage_invite", "Usage: /clan invite <player: player>"))
            return True

        target_name = args[0]
        target = self.plugin.server.get_player(target_name)
        if not target:
            msg = self.messages.get("player_not_found", "Player [player_name] not found.")
            msg = msg.replace("[player_name]", target_name)
            sender.send_error_message(msg)
            return True

        player = sender

        async def invite_task():
            try:
                xuid = int(player.xuid)
                clan = self.db.get_member_clan(xuid)
                
                if not clan:
                    self.scheduler.run_task(self.plugin, lambda: sender.send_error_message(self.messages.get("not_in_clan", "not in clan")))
                    return

                if clan.owner_xuid != xuid:
                    self.scheduler.run_task(self.plugin, lambda: sender.send_error_message(self.messages.get("not_the_owner", "not the owner")))
                    return

                target_xuid = int(target.xuid)
                target_clan = self.db.get_member_clan(target_xuid)
                if target_clan:
                    msg = self.messages.get("player_already_in_clan", "[player_name] is already in a clan.")
                    msg = msg.replace("[player_name]", target.name)
                    self.scheduler.run_task(self.plugin, lambda: sender.send_error_message(msg))
                    return

                cooldown_key = (str(xuid), str(target_xuid))
                now = time.time()
                if cooldown_key in self.plugin.invite_cooldowns:
                    if now - self.plugin.invite_cooldowns[cooldown_key] < 600:
                        msg = self.messages.get("invite_cooldown", "You must wait before inviting [player_name] again.")
                        msg = msg.replace("[player_name]", target.name)
                        self.scheduler.run_task(self.plugin, lambda: sender.send_error_message(msg))
                        return

                def on_form_submit(p: Player, index: int):
                    if index == 0:
                        async def accept_task():
                            if self.db.get_member_clan(int(p.xuid)):
                                return
                            
                            self.db.add_member(clan.owner_xuid, int(p.xuid))
                            msg = self.messages.get("invite_accepted", "You have joined [clan_name]!")
                            msg = msg.replace("[clan_name]", clan.display_name)
                            p.send_message(msg)
                            
                            inviter = self.plugin.server.get_player(player.name)
                            if inviter:
                                inviter.send_message(f"{p.name} joined your clan.")
                        
                        submit(accept_task())
                    else:
                        self.plugin.invite_cooldowns[cooldown_key] = time.time()
                        msg = self.messages.get("invite_declined", "[player_name] declined your invitation.")
                        msg = msg.replace("[player_name]", p.name)
                        inviter = self.plugin.server.get_player(player.name)
                        if inviter:
                            inviter.send_message(msg)

                form = MessageForm(
                    title=self.messages.get("invite_received_title", "Clan Invitation"),
                    content=self.messages.get("invite_received_content", "[player_name] invited you to join [clan_name].")
                    .replace("[player_name]", player.name)
                    .replace("[clan_name]", clan.display_name),
                    button1=self.messages.get("invite_yes", "Yes"),
                    button2=self.messages.get("invite_no", "No"),
                    on_submit=on_form_submit
                )
                
                self.scheduler.run_task(self.plugin, lambda: target.send_form(form))
                
                msg = self.messages.get("invite_sent", "Invitation sent to [player_name].")
                msg = msg.replace("[player_name]", target.name)
                self.scheduler.run_task(self.plugin, lambda: sender.send_message(msg))

            except Exception as e:
                raise e

        self._submit_and_handle_future_result(invite_task())
        return True

    def kick(self, sender: CommandSender, command: Command, args: list[str]):
        raise NotImplementedError

    def leave(self, sender: CommandSender, command: Command, args: list[str]):
        if not isinstance(sender, Player):
            sender.send_error_message(self.messages.get("not_a_player", "Only players can use this command."))
            return True

        async def leave_task():
            try:
                xuid = int(sender.xuid)
                clan = self.db.get_member_clan(xuid)
                
                if not clan:
                    self.scheduler.run_task(self.plugin, lambda: sender.send_error_message(self.messages.get("not_in_clan", "not in clan")))
                    return

                if clan.owner_xuid == xuid:
                    self.db.delete_clan(xuid)
                    msg = self.messages.get("clan_disbanded", "clan disbanded")
                    msg = msg.replace("[clan_name]", clan.display_name)
                    self.scheduler.run_task(self.plugin, lambda: sender.send_message(msg))
                else:
                    self.db.remove_member(clan.owner_xuid, xuid)
                    msg = self.messages.get("clan_left", "clan disbanded")
                    msg = msg.replace("[clan_name]", clan.display_name)
                    self.scheduler.run_task(self.plugin, lambda: sender.send_message(msg))
            except Exception as e:
                raise e

        self._submit_and_handle_future_result(leave_task())
        return True

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