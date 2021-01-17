import unittest

from engine import ai
from engine.globals import G
from tests import common


class _MockEvent:
    
    def __init__(self, tag):
        self._tag = tag

    def __eq__(self, other):
        return self._tag == other._tag

    def __hash__(self):
        return hash(hash(self._tag) + hash(type(self)))


class AiTest(common.EngineTest):

    def test_hates_player(self):
        hateful = ai.HatesPlayer()
        action = hateful.choose_action(G.player.current_room)
        attack = action.attack
        self.assertIs(G.player, attack.target)
        self.assertIsNone(attack.method)

    def test_chill(self):
        chill = ai.Chill()
        on_aesthetic_bliss = _MockEvent('bliss')
        default = _MockEvent('default')
        chill.add_event(on_aesthetic_bliss, 'aesthetic_bliss')
        chill.add_default_event(default)

        # TODO: .event.event is obnoxious; make a pass-through method?
        self.assertEquals(
            on_aesthetic_bliss,
            chill.choose_action(G.player.current_room, 'aesthetic_bliss').event.event)
        self.assertEquals(
            default,
            chill.choose_action(G.player.current_room, 'ennui').event.event)
