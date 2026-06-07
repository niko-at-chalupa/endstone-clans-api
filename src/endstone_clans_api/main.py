from pathlib import Path
from typing import Any, cast
from endstone.plugin import Plugin
from pydantic import BaseModel, Field
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

class ClansConfig(BaseModel):
    messages: dict[str, str] = Field(default_factory=dict)

class ClansApiPlugin(Plugin):
    api_version = "0.11"
    _config: ClansConfig

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
        self._config = self._load_config()
        self.register_events(self)
        self.logger.info("Clans API Plugin enabled.")

    @property
    def config(self) -> ClansConfig:
        return cast(ClansConfig, self._config)

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
