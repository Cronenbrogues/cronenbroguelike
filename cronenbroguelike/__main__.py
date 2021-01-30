import logging

from cronenbroguelike import util


logging_config = util.read_overridable_config("logging_config.default.json")
logging.basicConfig(level=getattr(logging, logging_config["log_level"].upper()))


from . import game


game.main()
