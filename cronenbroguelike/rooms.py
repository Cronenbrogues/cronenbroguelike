import copy
import random

from engine import dice
from engine.event import Event as _Event
from engine.globals import G
from engine.room import Room as _Room
from engine import say


_THEME_TO_ROOMS = {}
_ALL_ROOMS = []


def _create_room(*args, **kwargs):
    # TODO: Make a registry or something for this.
    result = _Room(*args, **kwargs)
    _THEME_TO_ROOMS.setdefault(result.theme, set()).add(result)
    _ALL_ROOMS.append(result)
    return result


# TODO: Devise a way to load rooms (and maybe events?) from a config file.
cathedral = _create_room("You are in a cathedral.", theme="cathedral")


iron_womb = _create_room(
    "You are squatting in a humid, low-ceilinged room made of rusted iron.",
    theme="biopunk",
)


class _AcidDropEvent(_Event):

    def execute(self):
        if dice.roll('1d100') > 90:
            say.insayne("A drop of acid falls on your head.")
            G.player.health.heal_or_harm(-1 * dice.roll('1d2'))


acid_room = _create_room(
        "You are in a large chamber. The ground and walls are like gristle. "
        "A sphincter on the ceiling occasionally drips into a fetid pit.",
        theme="behemoth")
acid_room.add_event(_AcidDropEvent())


class _IntestineRoomEvent(_Event):

    def execute(self):
        say.insayne(
            "You are in a dark tube. The walls and floor quiver at your touch, "
            "and you realize this is the intestine of a vast behemoth."
        )

        G.player.insanity.modify(10)
        self.room.description = (
            "The walls and floor of the intestine room shudder at your step."
        )
        self._will_execute = False


intestine_room = _create_room("", theme="behemoth")
intestine_room.add_event(_IntestineRoomEvent())


def all_rooms():
    # TODO: Don't do this via copies. Maybe use getter functions. Maybe just
    # use inheritance.
    return copy.deepcopy(_ALL_ROOMS)
