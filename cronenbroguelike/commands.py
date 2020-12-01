import re

import adventurelib

from engine.globals import G
from engine import say


def enter_room(room):
    """Convenience function called at game start and when entering a room."""
    for event in room.events():
        event.execute()
    look()


@adventurelib.when("exit DIRECTION")
@adventurelib.when("go DIRECTION")
@adventurelib.when("proceed DIRECTION")
@adventurelib.when("north", direction="north")
@adventurelib.when("south", direction="south")
@adventurelib.when("east", direction="east")
@adventurelib.when("west", direction="west")
def go(direction):
    # TODO: What about text associated with the movement other than just "you
    # go here"?
    direction = direction.lower()
    next_room = G.current_room.exit(direction)
    if next_room is None:
        say.insayne(f"It is not possible to proceed {direction}.")
    else:
        G.enqueue_text(f"You proceed {direction}.")
        G.current_room = next_room
        enter_room(G.current_room)


@adventurelib.when("look")
def look():
    G.enqueue_text(G.current_room.description)
    G.enqueue_text(f'Exits are {", ".join(G.current_room.exits)}.')

    for i, text in enumerate(G.generate_text()):
        if i > 0:
            adventurelib.say("")
        say.insayne(text)


@adventurelib.when("stats")
def stats():
    for stat_name, stat_value in G.player.all_stats():
        say.insayne(f"{stat_name:10}: {stat_value}")


@adventurelib.when("cheat CODE")
def cheat(code):
    m = re.search(r"([a-zA-Z]+)\s+(\-?\d+)", code)
    if m is None:
        return

    stat, delta = m.groups()
    stat = stat.lower()
    delta = int(delta)
    G.player.mod_stat(stat, delta)
    adventurelib.say(
        f"{stat.title()} {'in' if delta >= 0 else 'de'}creased by {delta}."
    )
