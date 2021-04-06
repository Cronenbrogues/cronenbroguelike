import logging
import os

from . import util


logging_config = util.read_config(util.ConfigType.LOGGING)
logging.basicConfig(level=getattr(logging, logging_config["log_level"].upper()))


from . import game


game.main()
