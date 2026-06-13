from endstone_clans_api.commands import ClansCommands
from pathlib import Path
from typing import Any, cast
from endstone.plugin import Plugin
from pydantic import BaseModel, Field
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from .database import Database, _Database
from endstone.command import Command, CommandSender
from .api import ClansApi

class ClansConfig(BaseModel):
    messages: dict[str, str] = Field(default_factory=dict)
    help: dict[str, str] = Field(default_factory=dict)

class ClansApiPlugin(Plugin):
    api_version = "0.11"
    _config: ClansConfig
    _api: ClansApi | None = None

    commands = {
        "clan": {
            "description": "Manage or create a clan",
            "usages": [
                "/clan <subcommand: string> [args: message]",
                "/clan help",
                "/clan create <name: str>",
                "/clan rename <name: str>",
                "/clan invite <player: player>",
                "/clan kick <player: player>",
                "/clan leave",
            ],
            "permissions": ["clans-api.command"],
        }
    }

    permissions = {
        "clans-api.command": {
            "description": "Base permission for all endstone clans API commands",
            "default": True,
        }
    }

    def on_enable(self):
        self.data_folder.mkdir(exist_ok=True)
        self._config = self._load_config()
        self._db = _Database(self, self.data_folder / "clans.db")
        self.register_events(self)
        self.clans_commands = ClansCommands(self)
        self._api = ClansApi(self)

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        if command.name != "clan":
            return False

        if len(args) == 0:
            sender.send_error_message(self.config.messages.get("no_subcommand", "no subcommand"))
            return False
    
        subcommand = self.clans_commands.subcommand_map.get(args[0])
        if not subcommand:
            sender.send_error_message(self.config.messages.get("invalid_subcommand", "invalid subcommand"))
            return False

        try:
            # args[1] is actually just a string of the rest of the args
            # since we take in a "message" type. We have to manually split.
            return subcommand(sender, command, args[1].split() if len(args) > 1 else [])
        except Exception as e:
            self.logger.error(f"ERROR !!!!!!!!!!!!! 😭😭😭 While handling subcommand `{args[0]}` for `{sender.name}`!! 🥺🥺🥺")                
            self.logger.error(str(e))
            
            sender.send_error_message(self.config.messages.get("generic_error", "generic error"))

            return False

    @property
    def config(self) -> ClansConfig:
        return self._config

    @property
    def api(self) -> ClansApi | None:
        return self._api

    @property
    def db(self) -> Database:
        return self._db

    def _load_config(self) -> ClansConfig:
        folder = Path(self.data_folder)
        folder.mkdir(parents=True, exist_ok=True)
        cfg_path = folder / "config.yml"
        
        yml = YAML()
        yml.version = (1, 2)
        yml.preserve_quotes = False
        
        defaults = [
            ("messages.no_permission", "You do not have permission to use this command.", "Message shown when a player lacks permission"),
            ("messages.clan_created", "Clan [clan_name] has been successfully created!", "Message shown when a clan is created"),
            ("messages.no_subcommand", "No subcommand was provided. Try /clans help.", "Shown when /clans is used with no arguments"),
            ("messages.invalid_subcommand", "The subcommand provided isn't valid. Try /clan help.", "Shown when /clan is used with an invalid subcommand"),
            ("messages.generic_error", "A technical error has occoured. Please contact a server admin or owner.", "Generic error for commands"),
            ("messages.not_a_player", "Only players can use this command.", "Message shown when a non-player uses a player-only command"),
            ("messages.already_in_clan", "You're already in a clan!", "Message shown when a player tries to join/create a clan while in one"),
            ("messages.clan_name_taken", "A clan with that name already exists!", "Message shown when a clan name is already in use"),
            ("messages.usage_create", "Usage: /clan create <name>", "Message shown when /clan create is used incorrectly"),
            ("messages.not_in_clan", "You're not in a clan!", "Message shown when a player tries to use a clan command but isn't in one"),
            ("messages.clan_left", "You have left the clan [clan_name].", "Message shown when a player leaves a clan"),
            ("messages.clan_disbanded", "Your clan [clan_name] has been disbanded.", "Message shown when a clan is disbanded because the owner left"),
            ("messages.help_header", "--- Clan Help ---", "Goes atop the help area."),
            ("messages.not_in_a_clan", "You are NOT in a clan!!", "Message shown when player attempts to do a clan-related action when NOT in a clan."),
            ("messages.not_the_owner", "You're NOT the owner of the clan!!", "Message shown when player attempts to do a clan-related action when NOT the owner."),
            ("messages.clan_name_already_taken", "That name is already taken!", "Message shown to players if a clan name is already taken."),

            # Everything underneath the help.* namespace is the help description for the
            # command specified.
            ("help.help", "Show this help message", "/clan help"),
            ("help.rename", "Rename a clan. Example: /clan rename \"my old clan\" \"my new one\"", "/clan rename"),
            ("help.invite", "Invite a player to your clan", "/clan invite"),
            ("help.kick", "Remote a player from your clan", "/clan kick"),
            ("help.leave", "Makes you leave the clan you're in. If you're the owner of the clan you leave, then the clan will be deleted.", "/clan leave")
        ]
        
        if cfg_path.exists():
            with open(cfg_path, "r", encoding="utf-8") as f:
                existing = yml.load(f)
            if not isinstance(existing, CommentedMap):
                existing = CommentedMap(existing or {})
        else:
            existing = CommentedMap()

        for key, default, comment in defaults:
            keys = key.split(".")
            current = existing
            for i, k in enumerate(keys[:-1]):
                if k not in current:
                    current[k] = CommentedMap()
                current = current[k]
            
            if keys[-1] not in current:
                current[keys[-1]] = default
                current.yaml_add_eol_comment(comment, keys[-1])

        with open(cfg_path, "w", encoding="utf-8") as f:
            yml.dump(existing, f)

        config_dict = self._commented_map_to_dict(existing)
        return ClansConfig(**config_dict)

    def _commented_map_to_dict(self, data: Any) -> Any:
        if isinstance(data, CommentedMap):
            return {k: self._commented_map_to_dict(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._commented_map_to_dict(v) for v in data]
        return data
