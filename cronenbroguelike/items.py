import logging
import random

from engine.event import Event as _Event
from engine.globals import G as _G
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
        return cls("cigarette butt")


class CigaretteStub(_Consumable):

    def consume(self, consumer):
        if not consumer.inventory.find('lighter'):
            say.insayne(f'You have no way to light the {self.name}.')
            return

        if consumer is _G.player:
            say.insayne(
                    f"You take a furtive puff on the {self.name}. It tastes foul "
                    "and acrid. You do not feel like you are wearing a leather "
                    "jacket at all.")
            consumer.health.heal_or_harm(- dice.roll("2d2"), cause="smoking half a cig")
        else:
            name = consumer.name[0].upper() + consumer.name[1:]
            say.insayne(f"{name} puffs furtively on a {self.name}.")
        
        consumer.inventory.remove(self)
        cigarette_butt = CigaretteButt.create()
        consumer.inventory.add(cigarette_butt)
        consumer.current_room.items.add(Smoke.create(consumer.current_room))

    @classmethod
    def create(cls):
        return cls("cigarette stub", "stub")


class Cigarette(_Consumable):

    def consume(self, consumer):
        if not consumer.inventory.find('lighter'):
            say.insayne(f'You have no way to light the {self.name}.')
            return

        # TODO: Customize text based on whether consumer is player.
        # TODO: Add location to actors so that the state of onlookers can
        # be properly assessed.
        aliases = random.sample(self.aliases, 2)
        if consumer is _G.player:
            say.insayne(
                    f"You take a long, smooth drag on the {aliases[0]}. Time seems "
                    "to mellow; all activity nearby slows. Onlookers watch as you "
                    "draw measured, pensive little puffs from the delicious "
                    f"{aliases[1]}. You look very cool.")
            consumer.health.heal_or_harm(- dice.roll("1d2"), cause="being cool")
        else:
            name = consumer.name[0].upper() + consumer.name[1:]
            say.insayne(f"{name} puffs mellowly on a {self.name}, looking extremely fly.")

        # TODO: Buff strength for a little bit.
        # TODO: Heal insanity, restore psyche.
        # TODO: I don't like this solution as it presumes the item is in the
        # consumer's inventory. Maybe that is a fine assumption. If not,
        # consider storing the inventory relationship as two-way.
        consumer.inventory.remove(self)
        cigarette_stub = CigaretteStub.create()
        consumer.inventory.add(cigarette_stub)
        consumer.current_room.items.add(Smoke.create(consumer.current_room))

    @classmethod
    def create(cls):
        return cls("cigarette", "coffin nail", "cancer stick")


class Lighter(_Item):
    
    @classmethod
    def create(cls):
        return cls("lighter")


class _FadingSmokeEvent(_Event):

    def execute(self):
        logging.debug("FadingSmokeEvent executing.")
        to_remove = []

        for item in self.room.items:
            if isinstance(item, FadingSmoke) or isinstance(item, Smoke):
                to_remove.append(item)

        if not to_remove:
            self.kill()

        for item in to_remove:
            if isinstance(item, FadingSmoke):
                self.room.items.remove(item)
            elif isinstance(item, Smoke):
                item.turns -= 1
                if item.turns <= 0:
                    self.room.items.add(FadingSmoke.create())
                    self.room.items.remove(item)


# TODO: Maybe make ephemeral items and have a global event that polls for them,
# changing their state?
class Smoke(_Item):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.turns = 2

    @classmethod
    def create(cls, room):
        event = _FadingSmokeEvent()
        room.add_event(event)
        _G.add_event(event, "post")
        return cls(
                "smoke", description="plumes of smoke",
                idle_description="Thick wreaths of acrid smoke hang in the air.")


class FadingSmoke(_Item):

    @classmethod
    def create(cls):
        return cls(
                "fading smoke", description="plumes of smoke",
                idle_description="A thin haze of smoke remains here.")
