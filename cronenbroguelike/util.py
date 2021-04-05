import enum
import json
import os.path
import re


from whimsylib.globals import G as _G


class ConfigType(enum.Enum):
    LOGGING = 0
    GAME = 1


_CONFIG_MAP = {
    ConfigType.LOGGING: ["logging_config.default.json", "logging_config.json"],
    ConfigType.GAME: ["game_config.default.json", "game_config.json"],
}


_CONFIG_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")


class _ConfigError(Exception):
    pass


def read_configs(default_file_name, override_file_name=None):
    if override_file_name is None:
        override_file_name = re.sub(r"\.default(\.json)$", r"\1", default_file_name)

    def _load(file_name):
        with open(file_name, "r") as inp:
            return json.load(inp)

    config = _load(default_file_name)
    if os.path.exists(override_file_name):
        config.update(_load(override_file_name))

    return config


def read_overridable_config(config_type):
    if config_type not in _CONFIG_MAP:
        raise _ConfigError()
    default_file_name, override_file_name = [
        os.path.join(_CONFIG_ROOT, file_name) for file_name in _CONFIG_MAP[config_type]
    ]
    return read_configs(default_file_name, override_file_name)
