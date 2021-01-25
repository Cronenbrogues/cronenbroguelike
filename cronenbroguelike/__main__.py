import json
import logging


def _configure_logging():
    with open("logging_config.json", "r") as inp:
        logging_config = json.load(inp)
    logging.basicConfig(level=getattr(logging, logging_config["log_level"].upper()))


_configure_logging()


from . import game


game.main()
