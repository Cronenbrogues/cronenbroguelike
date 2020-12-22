import json
import logging


def _configure_logging():
    logging_config = {"log_level": "INFO"}
    try:
        with open("logging_config.json", "r") as inp:
            additional_config = json.load(inp)
    except FileNotFoundError:
        additional_config = {}

    logging_config.update(additional_config)
    logging.basicConfig(level=getattr(logging, logging_config["log_level"].upper()))
    return logging_config


_configure_logging()


from . import game


game.main()
