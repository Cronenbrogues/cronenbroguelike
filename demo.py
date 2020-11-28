import random

import adventurelib

from src import directions
from src.globals import G
from src import room


def _create_room():
    descriptions = [
        'You are in a cathedral.',
        'You are squatting in a humid, low-ceilinged room made of rusted iron.',
        'You are in a dark tube. The walls and floor quiver at your touch, and '
        'you realize this is the intestine of a vast behemoth.',
    ]
    return room.Room(random.choice(descriptions))


G.current_room = initial_room = _create_room()
next_room = _create_room()
initial_room.add_exit(
    random.choice([
            directions.north, directions.south, directions.east,
            directions.west]),
    next_room)


@adventurelib.when('exit DIRECTION')
@adventurelib.when('go DIRECTION')
@adventurelib.when('proceed DIRECTION')
@adventurelib.when('north', direction='north')
@adventurelib.when('south', direction='south')
@adventurelib.when('east', direction='east')
@adventurelib.when('west', direction='west')
def go(direction):
    # TODO: What about text associated with the movement other than just "you
    # go here"?
    direction = direction.lower()
    next_room = G.current_room.exit(direction)
    if next_room is None:
        adventurelib.say(f'It is not possible to proceed {direction}.')
    else:
        G.enqueue_text(f'You proceed {direction}.')
        G.current_room = next_room
        look()


@adventurelib.when('look')
def look():
    # TODO: What if a room's description needs to change dynamically, e.g. on
    # subsequent entrances?
    G.enqueue_text(G.current_room.description)
    G.enqueue_text(f'Exits are {", ".join(G.current_room.exits)}.')

    for i, text in enumerate(G.generate_text()):
        if i > 0:
            adventurelib.say('')
        adventurelib.say(text)


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
            'a day, but the stubborn hope glisters in your mind.']:
        G.enqueue_text(text)


_get_random_start()


look()
adventurelib.say('')
adventurelib.start()
