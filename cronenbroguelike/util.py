import enum
import json
import os.path
import re
import importlib.resources


from whimsylib.globals import G as _G


class ConfigType(enum.Enum):
    LOGGING = 0
    GAME = 1


_CONFIG_MAP = {
    ConfigType.LOGGING: "logging_config.json",
    ConfigType.GAME: "game_config.json",
}


class _ConfigError(Exception):
    pass


def read_config(config_type):
    if config_type not in _CONFIG_MAP:
        raise _ConfigError()

    def _load(file_name):
        with importlib.resources.open_binary("config", file_name) as fh:
            data = json.load(fh)
        return data

    return _load(_CONFIG_MAP[config_type])
