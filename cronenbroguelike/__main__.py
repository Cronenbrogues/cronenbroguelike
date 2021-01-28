import json
import logging
import os


def _configure_logging():
    if os.path.exists("logging_config.json"):
        config_file = "logging_config.json"
    else:
        config_file = "logging_config.default.json"
    with open(config_file, "r") as inp:
        logging_config = json.load(inp)
    logging.basicConfig(level=getattr(logging, logging_config["log_level"].upper()))


_configure_logging()


from . import game


game.main()
