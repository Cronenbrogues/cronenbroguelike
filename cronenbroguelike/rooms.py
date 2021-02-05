import adventurelib
import logging
import random

from . import npcs
from engine import dice
from engine.event import Event as _Event
from engine.globals import G
from engine.room import Room as _Room
from engine import say


# TODO: Devise a way to load rooms (and maybe events?) from a config file.
# TODO: Create "locations" within each room to find items in, for enemies to
# hang out in, etc.
_CathedralPews = _Room.create_room_type(
    "CathedralPews",
    "You are in the pews of a maddening cathedral. The benches stretch on "
    "all sides and seem to creep up the walls. A murmuring sound suggests "
    "either wind or the prayers of an unseen petitioner.",
    themes=["cathedral"],
)
_CathedralCatacombs = _Room.create_room_type(
    "CathedralCatacombs",
    "You descend slick stairs into catacombs. Time-smooth placards adorn "
    "niches. The thick air smells of stone and moisture.",
    themes=["cathedral"],
)
_CathedralLibrary = _Room.create_room_type(
    "CathedralLibrary",
    "A crumbling library. Tomes of thick vellum stand open on tables. The "
    "chairs are askew. Distant laughter can be heard.",
    themes=["cathedral"],
)
_CathedralOffice = _Room.create_room_type(
    "CathedralOffice",
    "A desk is strewn with sheaves of paper. Little of sense is written there.",
    themes=["cathedral"],
)
# also have probabilities!
# and probabilities of nodes spawning too?
# cathedral_office.add_allowed_successor(cathedral_library, probability=0.25)
# cathedral_office.add_disallowed_successor(cathedral_catacombs)

# by default, a Room will connect with every other room of the same theme with equal probability
# maybe worth adding max_exits and min_exits params?

# how exactly do these probabilities work? if have 10 edges coming out, each with .25 chance of being created...
# do you not want them? or normalize?
# lets say each edge defaults to having a value of "1"
# then when choosing a new edge you sum up and choose
# also want a "no edge" thing? just None?

# so two rounds
# first, generate a set of nodes (Rooms) according to their probabilities and max/min values
# then, link rooms together according to their probabilties and min/max values
# but how to describe the edges?
# defaults:
# actually a bit complicated - want to be able to go "north, south, east, or west" to anything within the same theme
# and if have an edge going "north" somewhere, only want "south" coming back

# ok you're kind of making a graph with probabilistic edges, which then gets turned into a real graph?

# does this gain you much?
# maybe simpler to just allow rooms to add extra edges *on top* of the grid thing?
# like add_special_edge(room, probability, bidirectional)


class _BoilerHeatEvent(_Event):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._counter = 1

    def execute(self):
        if self._counter % 3 == 0:
            say.insayne("The heat is too much for you.")
            G.player.health.heal_or_harm(
                -1 * dice.roll("1d2"), cause="sweating in the boiler room"
            )
        self._counter += 1


class _BoilerRoom(_Room):

    _DESCRIPTION = (
        "A boiler sits in the center of this room. Its grate glows red. "
        "The air is intolerably hot."
    )
    _THEMES = ["cathedral"]

    def on_enter(self):
        super().on_enter()
        self._event = _BoilerHeatEvent()
        G.add_event(self._event, "post")

    def on_exit(self):
        super().on_exit()
        self._event.kill()


class _SongInHeadEvent(_Event):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._counter = 2

    def execute(self):
        say.insayne("🎵 MMMMMMMMBOP ba duba dop ba du dop DING DONG 🎵")
        self._counter -= 1
        if self._counter <= 0:
            self.kill()


class _BelfryEvent(_Event):

    _TURNS_TO_CHIME = 24

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._counter = -1

    def execute(self):
        self._counter += 1
        if self.room is not G.player.current_room:
            return
        if self._counter % self._TURNS_TO_CHIME == 0:
            say.insayne(
                "Suddenly, the bells begin to chime in simultaneity, if not "
                "exactly unison. From the chaos can be discerned a discordant "
                "melody. It is a blasphemous all-bells rendition of Hanson's "
                "'MMMBop.' As the final incomprehensible peal subsides, you "
                "realize the song is stuck in your head, threatening the "
                "sinews of your very sanity."
            )
            G.player.insanity.modify(15)
            G.add_event(_SongInHeadEvent(), "pre")


class _BelfryRoom(_Room):

    _DESCRIPTION = (
        "A disquieting array of bells hangs from the ceiling here. "
        "The clappers swing low, nearly grazing the top of your head. "
        "An unseen motive force sweeps through the bells at random, "
        "causing them to chime."
    )
    _THEMES = ["cathedral"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._event = None

    def on_enter(self):
        super().on_enter()
        if self._event is None:
            self._event = _BelfryEvent()
            self._event.room = self
            G.add_event(self._event, "post")

    def on_exit(self):
        super().on_exit()


class _AltarEvent(_Event):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute(self):
        smoke = self.room.items.find("smoke") or self.room.items.find("fading smoke")
        if smoke is not None:
            say.insayne(
                "The smoke whirls for a moment on the altar as though set "
                "there for an offering. "
                "The idol's ruby eyes seem to blaze as the smoke makes "
                "languorous curls beneath its nose. With a sound like the "
                "clatter of gravel and like the snuffling of many beasts, the "
                "idol draws the smoke into its nostrils. Its mouth shudders "
                "and falls open, smashing the altar beneath to shards. "
            )
            say.insayne("All beings present are pelted with debris.")
            for character in reversed(list(self.room.characters)):
                character.health.heal_or_harm(-1, cause="pelting with stone fragments")
            say.insayne(
                "In the idol's lax jaws can be seen a passage, like a pulsing "
                "throat, winding downward. From the throat you hear a voice "
                "like wet cloth dragged over stone: "
            )
            say.insayne("'You have practiced the first mortification")
            say.insayne("and shown you lack attachment to your health.", False)
            say.insayne("Through me you will find the way to the second.", False)
            say.insayne("Through me you will see your flesh as loathsome.'", False)
            say.insayne("These things will come to pass in their own time.", False)
            say.insayne("They may not now. The stars are not aligned.'", False)
            say.insayne(
                "Soon, this idol will lead you to horrors and blasphemies. "
                "For now, you must roam without succor and without end in this "
                "cathedral. Perhaps enjoy a cigarette with the enviably cool "
                "gentleman."
            )
            self.room.description = (
                "An idol with ruby eyes and a soot-stained maw yawns at you. "
                "Its throat, of an almost irritated red color, is large enough "
                "for you to pass through. The idol's mandible lies atop a pile "
                "of rubble. Fragments of stone are "
                "punctuated with the remains of an ivory frieze. One "
                "piece of ivory appears to depict the idol itself, its mouth "
                "cavernous, the red gold of its eyes showing contentment."
            )
            G.set_flag("IDOL_MOUTH_OPEN")
            self.room.items.remove(smoke)
            self.kill()


# TODO: Add a battle with a wrathful being if the smoker is slain.
class _AltarRoom(_Room):

    _DESCRIPTION = (
        "An idol with ruby eyes and a soot-stained maw sneers at you, showing "
        "carven fangs. Directly beneath its chin sits an altar, resting atop a "
        "stone plinth. Its sides are embellished with bas-relief ivory friezes "
        "depicting various acts both lewd and violent. On one side is depicted "
        "the apparent sacrifice of a man bearing a sprig of leaves, overseen by an angry "
        "beast. On another is shown a burnt offering of the same leaves. The smoke "
        "rises up toward a face, whose mouth gapes in a slack-jawed smile."
    )
    _THEMES = ["cathedral"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._event = None

    def on_enter(self):
        super().on_enter()
        if self._event is None:
            self._event = _AltarEvent()
            # TODO: Use add_event here and elsewhere;
            # omit _maybe_append_event from Room.add_event.
            self._event.room = self
            G.add_event(self._event, "post")
        adventurelib.set_context("altar")

    def on_exit(self):
        super().on_exit()
        adventurelib.set_context(None)


_Blank = _Room.create_room_type(
    "Blank",
    "A featureless room. The air tastes stale here. The walls and " "floor are sallow.",
)
_SittingRoom = _Room.create_room_type(
    "SittingRoom",
    "A gloomy expanse filled with furniture. You feel you are perhaps "
    "outdoors, though you see no sky or stars.",
)


_IronWomb = _Room.create_room_type(
    "IronWomb",
    "You are squatting in a humid, low-ceilinged room made of rusted iron.",
    themes=["biopunk"],
)


_RibRoom = _Room.create_room_type(
    "RibRoom",
    "You are standing on a slick, wet floor. The walls are a ribcage palisade. "
    "The room expands and contracts rhythmically.",
    themes=["behemoth"],
)


class _AcidDropEvent(_Event):
    def execute(self):
        if dice.roll("1d100") > 90:
            say.insayne("A drop of acid falls on your head.")
            G.player.health.heal_or_harm(
                -1 * dice.roll("1d2"), cause="being scalded with acid"
            )


class _AcidRoom(_Room):

    _DESCRIPTION = (
        "You are in a large chamber. Its center is dominated by a reeking, acidic "
        "sump. The walls around are like gristle. On the ceiling, an aperture "
        "occasionally drips pale liquid into the fetid pool."
    )
    _THEMES = ["behemoth"]

    def on_enter(self):
        super().on_enter()
        self._event = _AcidDropEvent()
        G.add_event(self._event, "post")

    def on_exit(self):
        super().on_exit()
        logging.debug(f"Killing event {self._event}.")
        self._event.kill()


# TODO: Attach events to the global queue, rather than to individual rooms.
# TODO: Poll for events after each command.
# TODO: Many behemoth rooms should induce insanity ...
# TODO: How to tie events to a specific room, though?
class _IntestineRoomEvent(_Event):
    def execute(self):
        # TODO: This kind of thing could be handled with a description generator.
        say.insayne(
            "You are in a dark tube. The walls and floor quiver at your touch, "
            "and you realize this is the intestine of a vast behemoth."
        )
        G.player.insanity.modify(10)
        # TODO: change to self.room.description
        G.player.current_room.description = (
            "The walls and floor of the intestine room shudder at your step."
        )
        self._will_execute = False


class _IntestineRoom(_Room):

    _DESCRIPTION = ""
    _THEMES = "behemoth"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._entered = False

    def on_enter(self):
        super().on_enter()
        if not self._entered:
            G.add_event(_IntestineRoomEvent(), "post")
            self._entered = True


# intestine_room = _IntestineRoom.create("", theme="behemoth")
# rib_room = _Room.create(
#     "You are standing on a slick, wet floor. The walls are a ribcage palisade. "
#     "The room expands and contracts rhythmically.",
#     theme="behemoth",
# )

class _BreakRoom(_Room):
    _DESCRIPTION = ""
    _THEMES = ["office"]


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_character(npcs.coffee_machine())
        self.add_character(npcs.gary())

    def on_enter(self):
        super().on_enter()


class _YourDesk(_Room):
    _DESCRIPTION = ""
    _THEMES = ["office"]


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_character(npcs.office_computer())
        self.add_character(G.player)

    def on_enter(self):
        super().on_enter()
        # G.player.insanity.modify(10)

# your_desk = _YourDesk.create("", themes=["office"])


class _CopierRoom(_Room):
    _DESCRIPTION = ""
    _THEMES = ["office"]


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_character(npcs.office_copier())

    def on_enter(self):
        super().on_enter()


class _MeetingRoom(_Room):
    _DESCRIPTION = ""
    _THEMES = ["office"]


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.add_character(npcs.office_copier())

    def on_enter(self):
        super().on_enter()
        insanity = G.player.insanity.value
        if insanity < 29:
            say.insayne("Meeting room description")
        else:
            say.insayne("Spawn meeting table")
            say.insayne("You are very insane")


# class _AssortedOfficeRoom(_Room):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#     def on_enter(self):
#         super().on_enter()
#         G.player.insanity.modify(10)
#         insanity = G.player.insanity.value
#         if insanity == 100:
#             say.insayne("You are totally insane")
#         elif insanity > 75:
#             say.insayne("You are very insane")
#         elif insanity > 50:
#             say.insayne("You are quite insane")
#         elif insanity > 25:
#             say.insayne("You are a bit insane")
#         elif insanity > 10:
#             say.insayne("You are a bit eccentric")
#         # say.insayne(f"insanity is currently {G.player.insanity.value}")
#         # if not self._entered:
#         #     G.add_event(_IntestineRoomEvent(), "post")
#         #     self._entered = True

# intestine_room = _OfficeRoom.create("", theme="office")

""" "office" theme ideas
- perfectly normal to start with
- things change when you walk by them multiple times
- after a while they start to increase insanity
- once insanity is high enough then you start seeing exits
- entities
  computer
  fax machine
  Gary
- items
  stapler
what if the entities (especially Gary) became exits themselves?
and then it becomes clear that you were inside some strange creature?

ok, maybe decrease will and increase insanity
think should go to 30 insanity max
that could mean three different "stages" - 0, 15, 30
or 4
4 seems good?
can you just add an exit when you want? think so

Gary could tell increasingly surreal dad jokes
should there be more Garys over time?

what if you added a "laugh" action that's only available in the office
and at first it just makes Gary tell you another joke
eventually Gary becomes some pitiful creature and you have to laugh at it to destroy it

rooms
- your desk
- copy room
- break room
- meeting room
- reception area

computer should become aggressive once insane enough
maybe if attack computer early on things get really weird?

ok, TODOs
- [X] add a few options of each thing! don't get too fancy yet, can flesh out later
- [X] add "your desk"
- [X] add "break room"
- [X] make "computer" actor and spawn it at your desk
- [X] add "use" action for computer
- [X] make "gary" actor
- [X] make gary tell bad jokes
- [X] use coffee machine -> get coffee
- [X] use coffee on gary -> he drinks it
- [X] use coffee on gary -> get ending if at 30 insanity
- [X] on restart, wake up at desk
- [X] make level consistent
- [X] make "use computer" give a bit of insanity
- [X] make copy machine, it can give a bit of insanity if >= 20
- [ ] add the meeting room
- [ ] hook up other strings
- [ ] try a playthrough
...
- [ ] make "enter gary" action
- [ ] make gary drink coffee on his own sometimes
- [ ] make computer kill you if you use at highest insanity

gary's jokes should turn to pleading
as they get darker and darker he should get grosser - "Gary laughs uproariously, spittle flying all over you."
change gary to larry?

what's the ending?
have to get ichor from coffee machine, use it in room with gary to "melt" him into a portal to the next floor?
if you use it on yourself it kills you
and you "jerk awake" at your desk
or maybe you have to use it on the computer?
or if you do something bad happens?

want copy machine?


ok, so first gary gives insanity
then computer
then copy machine (could give a few)?
what's a more surreal interaction? copy machine could do gross stuff
then finally final bit happens in the meeting room? could give you a hint to how to finish
could talk to the heap of bodies

how can you add flavor to make it clear that this is like an occult energy-harvesting operation?
"""

# can make tunnel when triggered

# could "wake up" in the office when transitioning there


def _rooms_for_theme(theme=None):
    if theme is None:
        return _Room.ALL_ROOMS
    return _Room.THEME_TO_ROOMS[theme]# + _Room.THEME_TO_ROOMS[_Room.DEFAULT_THEME]


def get_rooms(theme=None, number=None):
    room_types = _rooms_for_theme(theme)
    if number is not None:
        room_types = random.sample(room_types, number)
    return [room() for room in room_types]


def get_room(theme=None):
    return random.choice(_rooms_for_theme(theme))()
