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
    _THEME_TO_ROOMS.setdefault(result.theme, []).append(result)
    _ALL_ROOMS.append(result)
    return result


# TODO: Devise a way to load rooms (and maybe events?) from a config file.
# TODO: Create "locations" within each room to find items in, for enemies to
# hang out in, etc.
# TODO: Allow multiple themes.
cathedral_pews = _create_room(
        "You are in the pews of a maddening cathedral. The benches stretch on "
        "all sides and seem to creep up the walls. A murmuring sound suggests "
        "either wind or the prayers of an unseen petitioner.",
        theme="cathedral")
cathedral_catacombs = _create_room(
        "You descend slick stairs into catacombs. Time-smooth placards adorn "
        "niches. The thick air smells of stone and moisture.",
        theme="cathedral")
cathedral_library = _create_room(
        "A crumbling library. Tomes of thick vellum stand open on tables. The "
        "chairs are askew. Distant laughter can be heard.",
        theme="cathedral")
cathedral_office = _create_room(
        "A desk is strewn with sheaves of paper. Little of sense is written "
        "there.",
        theme="cathedral")


blank = _create_room(
        "A featureless room. The air tastes stale here. The walls and floor "
        "are sallow.")
sitting_room = _create_room(
        "A gloomy expanse filled with furniture. You feel you are perhaps "
        "outdoors, though you see no sky or stars.")


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


# TODO: Attach events to the global queue, rather than to individual rooms.
# TODO: Poll for events after each command.
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
rib_room = _create_room(
        "You are standing on a platform of gristle. A ribcage palisade "
        "surrounds you. The room expands and contracts rhythmically.",
        theme="behemoth")


def _rooms_for_theme(theme=None):
    if theme is None:
        return _ALL_ROOMS
    return _THEME_TO_ROOMS[theme] + _THEME_TO_ROOMS[_Room.DEFAULT_THEME]


def all_rooms(theme=None):
    # TODO: Don't do this via copies. Maybe use getter functions. Maybe just
    # use inheritance.
    return copy.deepcopy(_rooms_for_theme(theme))


def get_room(theme=None):
    return random.choice(all_rooms(theme))
