import unittest

from engine import actor
from engine import item
from tests import common


class ItemTest(common.EngineTest):

    def test_default_description(self):
        name = 'forbidden tome'
        forbidden_tome = item.Item(name)
        self.assertEqual(f'a {name}', forbidden_tome.description)

    def test_default_idle_description(self):
        name = 'welcoming pamphlet'
        welcoming_pamphlet = item.Item(name)
        self.assertEqual(
                f'There is a {name} lying on the ground.',
                welcoming_pamphlet.idle_description)

    def test_init(self):
        name = 'ambiguous recipe book'
        alias = 'grandpa\'s grill secrets v1'
        description = 'a leather-bound recipe book smelling faintly of smoke'
        idle_description = 'Grandpa clutches a leather-bound recipe book.'

        # You can't have grandpa's secrets.
        recipes = item.Item(
                name, alias, description=description,
                idle_description=idle_description, obtainable=False)

        self.assertEqual(name, recipes.name)
        self.assertEqual([name, alias], list(recipes.aliases))
        self.assertEqual(description, recipes.description)
        self.assertEqual(idle_description, recipes.idle_description)
