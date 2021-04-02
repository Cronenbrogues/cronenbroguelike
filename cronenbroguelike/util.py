import json
import os.path
import re


from whimsylib.globals import G as _G

CONFIGS = "config"

def read_overridable_config(default_file_name, override_file_name=None):
    if override_file_name is None:
        override_file_name = re.sub(r"\.default(\.json)$", r"\1", default_file_name)

    def _load(file_name):
        with open(os.path.join(CONFIGS, file_name), "r") as inp:
            return json.load(inp)

    config = _load(default_file_name)
    if os.path.exists(override_file_name):
        config.update(_load(override_file_name))

    return config
