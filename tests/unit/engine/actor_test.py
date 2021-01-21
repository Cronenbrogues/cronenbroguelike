import unittest
from unittest.mock import Mock
from unittest.mock import patch

from engine import actor
from engine.globals import G
from engine import room
from engine import tartarus
from tests import common


class ActorTest(common.EngineTest):

    @patch("engine.actor.say.insayne")
    def test_player_dies(self, mock_say):
        abattoir = room.Room.create()
        abattoir.add_character(G.player)

        with self.assertRaises(tartarus.RaptureException):
            G.player.die(cause="misadventure")
            mock_say.assert_called_once_with("You die.")
            mock_say.assert_called_once_with("...")
        self.assertEqual("misadventure", G.cause_of_death)

    def test_npc_dies(self):
        lou_dobbs = actor.create_actor(10, 10, 10, 10, 10, 10, "Lou Dobbs")

        # Put Lou Dobbs in a skeezy hotel.
        hotel_room = room.Room.create()
        hotel_room.add_character(lou_dobbs)

        # TODO: Add a fixture for adding characters to a room.
        # Or find another way to enshrine preconditions in tests.
        assert lou_dobbs in hotel_room.characters
        assert lou_dobbs not in hotel_room.corpses

        death_throes = Mock()
        lou_dobbs.upon_death(death_throes)

        # Let Lou Dobbs die alone in that ignominious, feculent, syphilitic hotel room.
        lou_dobbs.die()
        self.assertEqual(False, lou_dobbs.alive)
        death_throes.assert_called_once_with(lou_dobbs)
        self.assertIn(lou_dobbs, hotel_room.corpses)
        self.assertNotIn(lou_dobbs, hotel_room.characters)
