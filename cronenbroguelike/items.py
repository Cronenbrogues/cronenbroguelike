import random

from engine.item import Book as _Book
from engine.item import Consumable as _Consumable
from engine.item import Item as _Item
from engine import dice
from engine import say

from cronenbroguelike import ability


# TODO: Make this equippable.
class CeremonialKnife(_Item):

    @classmethod
    def create(cls):
        return cls("ceremonial knife", "knife", "kris")


class MeditationBook(_Book):

    def read(self, actor):
        if actor.has_read(self):
            # TODO: Condition pronoun/verb agreement on whether actor is
            # player or not. Make a utility function for this.
            say.insayne(
                "You have already tasted the wisdom distilled in this book."
            )

        else:
            actor.add_ability(ability.meditation)
            actor.set_has_read(self)

    @classmethod
    def create(cls):
        # TODO: "Book" might cause collisions. Handle ambiguity in commands
        # when more than one item has the same alias.
        return cls("meditation tome", "meditation book", "tome", "book")


class CigaretteButt(_Consumable):

    def consume(self, consumer):
        # TODO: Customize text based on whether consumer is player.
        say.insayne(f"You eat the {self.name}. What is wrong with you?")
        consumer.insanity.modify(10)
        consumer.inventory.remove(self)

    @classmethod
    def create(cls):
        return cls("cigarette butt", "smoke")


class CigaretteStub(_Consumable):

    def consume(self, consumer):
        # TODO: Customize text based on whether consumer is player.
        say.insayne(
                f"You take a furtive puff on the {self.name}. It tastes foul "
                "and acrid. You do not feel like you are wearing a leather "
                "jacket at all.")
        consumer.health.heal_or_harm(- dice.roll("2d2"))
        consumer.inventory.remove(self)
        consumer.inventory.add(CigaretteButt.create())

    @classmethod
    def create(cls):
        return cls("cigarette stub", "smoke")


class Cigarette(_Consumable):

    def consume(self, consumer):
        # TODO: Customize text based on whether consumer is player.
        # TODO: Add location to actors so that the state of onlookers can
        # be properly assessed.
        aliases = random.sample(self.aliases, 2)
        say.insayne(
                f"You take a long, smooth drag on the {aliases[0]}. Time seems "
                "to mellow; all activity nearby slows. Onlookers watch as you "
                "draw measured, pensive little puffs from the delicious "
                f"{aliases[1]}. You look very cool.")
        # TODO: Buff strength for a little bit.
        consumer.health.heal_or_harm(- dice.roll("1d2"))
        # TODO: I don't like this solution as it presumes the item is in the
        # consumer's inventory. Maybe that is a fine assumption. If not,
        # consider storing the inventory relationship as two-way.
        consumer.inventory.remove(self)
        consumer.inventory.add(CigaretteStub.create())

    @classmethod
    def create(cls):
        return cls("cigarette", "smoke", "coffin nail", "cancer stick")
