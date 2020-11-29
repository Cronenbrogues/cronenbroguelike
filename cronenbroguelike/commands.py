import re

import adventurelib

from engine.globals import G
from engine import say


def enter_room(room):
    """Convenience function called at game start and when entering a room."""
    # TODO: Find a better solution here. When the room's description changes
    # after an event, it should be possible not to repeat it.
    for event in room.events():
        event.execute()
    look()


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
        say.insayne(f'It is not possible to proceed {direction}.')
    else:
        G.enqueue_text(f'You proceed {direction}.')
        G.current_room = next_room
        enter_room(G.current_room)


@adventurelib.when('look')
def look():
    # TODO: What if a room's description needs to change dynamically, e.g. on
    # subsequent entrances?
    G.enqueue_text(G.current_room.description)
    G.enqueue_text(f'Exits are {", ".join(G.current_room.exits)}.')

    for i, text in enumerate(G.generate_text()):
        if i > 0:
            adventurelib.say('')
        say.insayne(text)


@adventurelib.when('stats')
def stats():
    statistics = ['insanity']
    for stat in statistics:
        say.insayne(f'{stat}:\t{getattr(G.player, stat)}')


@adventurelib.when('cheat CODE')
def cheat(code):
    m = re.search(r'insanity (\-?\d+)', code)
    if m is not None:
        insanity_delta = int(m.groups()[0])
        G.player.insanity += insanity_delta
        adventurelib.say(
                f'Insanity {"in" if insanity_delta >= 0 else "de"}creased '
                f'by {insanity_delta}.')
