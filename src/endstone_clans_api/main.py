from endstone_clans_api.commands import ClansCommands
from pathlib import Path
from typing import Any, cast
from endstone.plugin import Plugin
from pydantic import BaseModel, Field
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from .database import _Database
from endstone.command import Command, CommandSender

class ClansConfig(BaseModel):
    messages: dict[str, str] = Field(default_factory=dict)
    help: dict[str, str] = Field(default_factory=dict)

class ClansApiPlugin(Plugin):
    api_version = "0.11"
    _config: ClansConfig

    commands = {
        "clan": {
            "description": "Manage or create a clan",
            "usages": [
                "/clan <subcommand: string> [args: message]",
                "/clan help",
                "/clan create <name: str>",
                "/clan rename <old_name: str> <new_name: str>",
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
            "default": "op",
        }
    }

    def on_enable(self):
        self.data_folder.mkdir(exist_ok=True)
        self._config = self._load_config()
        self._db = _Database(self.data_folder / "clans.db")
        self.register_events(self)
        self.clans_commands = ClansCommands(self)

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
    def db(self) -> _Database:
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
            ("messages.help_header", "--- Clan Help ---", "Goes atop the help area."),

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
