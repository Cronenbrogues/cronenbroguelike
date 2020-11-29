import random

import adventurelib

from cronenbroguelike import commands
from engine import directions
from engine.event import Event
from engine.globals import G
from engine.room import Room
from engine import say


class _MeatRoomEvent(Event):
    
    def execute(self):
        say.insayne(
            'You are in a dark tube. The walls and floor quiver at your touch, '
            'and you realize this is the intestine of a vast behemoth.')

        # TODO: Find a better solution for this--better to have a single say func.
        adventurelib.say('')

        # TODO: Add the log in the insanity setter instead of here.
        G.player.insanity += 10
        say.insayne('Your insanity increases by 10.')
        adventurelib.say('')
        self.room.description = (
                'The walls and floor of the intestine room shudder at your '
                'step.')
        self._will_execute = False


def _create_rooms(number_of_rooms):
    rooms = [
        Room('You are in a cathedral.'),
        Room(
            'You are squatting in a humid, low-ceilinged room made of rusted '
            'iron.'),
    ]
    meat_room = Room(
        'You are in a dark tube. The walls and floor quiver at your touch, and '
        'you realize this is the intestine of a vast behemoth.')
    meat_room.add_event(_MeatRoomEvent())
    rooms.append(meat_room)
    return random.sample(rooms, number_of_rooms)


G.current_room, room_2, room_3 = _create_rooms(3)
possible_exits = [
        directions.north, directions.south, directions.east, directions.west]
exit_1 = random.choice(possible_exits)
room_2.add_exit(exit_1, G.current_room)
room_2.add_exit(
    random.choice(list(set(possible_exits) - set([exit_1]))), room_3)


def _get_random_start():
    cause_of_death = random.choice([
       'being impaled',
       'slowly suffocating as a glabrous tentacle horror looks on',
    ])
    for text in [
            f'The memory of {cause_of_death} fades away.',
            'You know only that you have been here for interminable years, '
            'that you have died innumerable times, and that someone once told '
            'you there was a way out. You were told this an eon ago, or maybe '
            'a day, but the stubborn hope of escape glisters in your mind.']:
        say.insayne(text)
        adventurelib.say('')


_get_random_start()


commands.enter_room(G.current_room)
adventurelib.say('')
adventurelib.start()
