import unittest
from unittest.mock import patch

from engine import dice


class _MockRandom:
    def __call__(self, x, y):
        return x + y


class DiceTest(unittest.TestCase):
    def test_roll_parses_expression(self):
        with patch("random.randint", new_callable=_MockRandom):
            self.assertEqual(4, dice.roll("d3"))
            self.assertEqual(3, dice.roll("1d2"))
            self.assertEqual(4, dice.roll("2d1"))

    def test_roll_range(self):
        possible_values = set(range(1, 11))
        for _ in range(100):
            self.assertIn(dice.roll("d10"), possible_values)
