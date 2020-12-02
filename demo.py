import random

import adventurelib

from cronenbroguelike import commands
from engine import actor
from engine import ai
from engine import directions
from engine.event import Event
from engine.globals import G
from engine.room import Room
from engine import say


class _MeatRoomEvent(Event):
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


def _create_rooms(number_of_rooms):
    rooms = [
        Room("You are in a cathedral."),
        Room(
            "You are squatting in a humid, low-ceilinged room made of rusted iron."
        ),
    ]
    meat_room = Room(
        "You are in a dark tube. The walls and floor quiver at your touch, and "
        "you realize this is the intestine of a vast behemoth."
    )
    meat_room.add_event(_MeatRoomEvent())
    rooms.append(meat_room)
    return random.sample(rooms, number_of_rooms)


def _get_random_start():
    cause_of_death = random.choice(
        [
            "being impaled",
            "slowly suffocating as a glabrous tentacle horror looks on",
        ]
    )
    for text in [
        f"The memory of {cause_of_death} fades away.",
        "You know only that you have been here for interminable years, "
        "that you have died innumerable times, and that someone once told "
        "you there was a way out. You were told this an eon ago, or maybe "
        "a day, but the stubborn hope of escape glisters in your mind.",
    ]:
        say.insayne(text)


def _start_game(_):

    # Creates the player character and ensures game will restart upon death.
    G.player = actor.create_actor(
        health=10, psyche=10, strength=10, stamina=10, will=10, wisdom=10,
        insanity=0, name="player"
    )
    G.player.log_stats = True
    G.player.upon_death(_start_game)

    # Creates a small dungeon.
    G.current_room, room_2, room_3 = _create_rooms(3)
    possible_exits = [
            directions.north, directions.south, directions.east, directions.west]
    exit_1 = random.choice(possible_exits)
    room_2.add_exit(exit_1, G.current_room)
    room_2.add_exit(
        random.choice(list(set(possible_exits) - set([exit_1]))), room_3)

    # Places a monster in a random room.
    _monster = actor.create_actor(
        health=10,
        psyche=10,
        strength=10,
        stamina=10,
        will=10, wisdom=10, insanity=100, name="Fish Man",
        ai=ai.HatesPlayer())

    # TODO: Make a Monster class (or component) that encapsulates this behavior.
    # TODO: Store location as a member of Actors and Items. That way, monsters can
    # run away bleeding or something and die where they are, rather than being
    # presumed to die in the current room. Alternately, simply change how attacking
    # works when monsters are dead.
    #
    # TODO: Why isn't .alive = False working?
    def fish_man_death_throes(fish_man):
        say.insayne(
            f'{fish_man.name} flops breathlessly upon the ground, blood '
            'commingling with piscine slobber. Half-formed gills flutter '
            'helplessly, urgently, then fall slack.')
        fish_man.alive = False

    _monster.upon_death(fish_man_death_throes)
    random.choice([G.current_room, room_2, room_3]).add_character(_monster)

    # Starts it up.
    _get_random_start()
    commands.enter_room(G.current_room)


_start_game(None)
G.player.upon_death(_start_game)
adventurelib.say('')  # Necessary for space before first prompt.
adventurelib.start()
