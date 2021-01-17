import unittest

from engine import actor
from engine.globals import G


class EngineTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        # G.player must always exist.
        G.player = actor.create_actor(10, 10, 10, 10, "player")
