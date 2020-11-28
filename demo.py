import random
import re

import adventurelib
import zalgo_text

from src import directions
from src.globals import G
from src import room


_Z = zalgo_text.zalgo()


_VOICES = [
    'HEEEHEHEHEHEHE',
    'THERE IS NO HOPE',
    'DID YOU HEAR THAT?',
    'I PROMISE YOU KNOWLEDGE',
]


def insayne(text):
    """Renders @text to screen, modified based on player's insanity stat.
    
    Interpolates arcane markings and violent exhortations if player's sanity
    is not pristine. Renders UI text less and less legible as sanity degrades.
    """
    if G.player.insanity < 30:
        adventurelib.say(text)
        return

    _Z.maxAccentsPerLetter = max(0, int((G.player.insanity - 20) / 10))
    num_breaks = int((G.player.insanity - 40) / 10)
    breakpoints = []
    if num_breaks > 0:
        breaks = [0]
        breaks.extend(sorted(random.sample(range(len(text)), num_breaks)))
        breaks.append(len(text))
        breakpoints.extend(zip(breaks[:-1], breaks[1:]))
    else:
        breakpoints.append((0, len(text)))

    segments = []
    for i, (begin, end) in enumerate(breakpoints):
        if i > 0:
            segments.append(random.choice(_VOICES))
        segments.append(_Z.zalgofy(text[begin:end]))

    adventurelib.say(''.join(segments))


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
        insayne(f'It is not possible to proceed {direction}.')
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
        insayne(text)


@adventurelib.when('stats')
def stats():
    statistics = ['insanity']
    for stat in statistics:
        insayne(f'{stat}:\t{getattr(G.player, stat)}')


@adventurelib.when('cheat CODE')
def cheat(code):
    m = re.search(r'insanity (\-?\d+)', code)
    if m is not None:
        insanity_delta = int(m.groups()[0])
        G.player.insanity += insanity_delta
        adventurelib.say(
                f'Insanity {"in" if insanity_delta >= 0 else "de"}creased '
                f' by {insanity_delta}.')


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
        G.enqueue_text(text)


_get_random_start()


look()
adventurelib.say('')
adventurelib.start()
