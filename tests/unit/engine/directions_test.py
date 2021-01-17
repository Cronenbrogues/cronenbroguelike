import unittest
from unittest.mock import patch

from engine import directions
from engine.globals import G
from tests import common


class DirectionsTest(common.EngineTest):

    def _test_oneway(self, direction, descriptions):
        self.assertEqual(descriptions[0], direction.display_description)
        self.assertEqual(descriptions, direction.descriptions)

    def test_make_oneway(self):
        descriptions = ['through a window', 'through somebody\'s window']
        direction = directions.Direction.make_oneway(descriptions)
        self._test_oneway(direction, descriptions)
        self.assertIsNone(direction.opposite)

    def test_make_twoway(self):
        descriptions = ['through a window', 'through somebody\'s window']
        reverse_descriptions = ['back through that window you broke']
        direction, opposite = directions.Direction.make_twoway(descriptions, reverse_descriptions)
        self._test_oneway(direction, descriptions)
        self._test_oneway(opposite, reverse_descriptions)
        self.assertIs(opposite, direction.opposite)
        self.assertIs(direction, opposite.opposite)

    def test_north_south(self):
        self._test_oneway(directions.north, ['north'])
        self._test_oneway(directions.south, ['south'])
        self.assertIs(directions.north, directions.south.opposite)
        self.assertIs(directions.south, directions.north.opposite)

    def test_east_west(self):
        self._test_oneway(directions.east, ['east'])
        self._test_oneway(directions.west, ['west'])
        self.assertIs(directions.east, directions.west.opposite)
        self.assertIs(directions.west, directions.east.opposite)

    def test_yellow_purple(self):
        self.assertIs(directions.yellow, directions.purple.opposite)
        self.assertIs(directions.purple, directions.yellow.opposite)
