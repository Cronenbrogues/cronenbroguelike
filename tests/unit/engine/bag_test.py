import unittest
from unittest.mock import patch

from engine import bag
from engine.globals import G
from engine import item

from tests import common


class BagAddAliasesTest(common.EngineTest):
    def test_add_aliases_adds_holder(self):
        backpack = bag.Bag()
        pamphlet = item.Item("sycophantic propaganda pamphlet")
        backpack.add(pamphlet)
        self.assertIs(backpack, pamphlet.holder)

    @patch("engine.actor.say.insayne")
    def test_add_aliases_message_for_player(self, mock_say):
        pamphlet = item.Item("sycophantic propaganda pamphlet")
        G.player.inventory.add(pamphlet)
        mock_say.assert_called_once_with(f"You acquire {pamphlet.name}.")

    # TODO: Might wants messages for NPCs someday, you know.
    @patch("engine.actor.say.insayne")
    def test_add_aliases_no_message_for_npc(self, mock_say):
        backpack = bag.Bag()
        pamphlet = item.Item("sycophantic propaganda pamphlet")
        backpack.add(pamphlet)
        mock_say.assert_not_called()


class BagDiscardAliasesTest(common.EngineTest):
    def setUp(self):
        self._pamphlet = item.Item("sycophantic propaganda pamphlet")
        G.player.inventory.add(self._pamphlet)

    def test_discard_aliases_removes_holder(self):
        G.player.inventory.remove(self._pamphlet)
        self.assertIsNone(self._pamphlet.holder)

    @patch("engine.actor.say.insayne")
    def test_discard_aliases_message_for_player(self, mock_say):
        G.player.inventory.remove(self._pamphlet)
        mock_say.assert_called_once_with(
            f"You lose possession of {self._pamphlet.name}."
        )

    def test_discard_aliases_no_message_for_npc(self):
        backpack = bag.Bag()
        backpack.add(self._pamphlet)
        self.assertIsNot(backpack, G.player.inventory)

        with patch("engine.actor.say.insayne") as mock_say:
            backpack.remove(self._pamphlet)
            mock_say.assert_not_called()
