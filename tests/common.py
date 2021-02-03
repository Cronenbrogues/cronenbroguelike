import unittest

from whimsylib import actor
from whimsylib.globals import G


class EngineTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        G.reset()
        # G.player must always exist.
        G.player = actor.create_actor(10, 10, 10, 10, "player")
