from adventurelib import when
from src.globals import G


@when("exit DIRECTION")
@when("north", direction="north")
@when("south", direction="south")
@when("east", direction="east")
@when("west", direction="west")
def go(direction):
    # TODO: What about text associated with the movement other than just "you
    # go here"?
    direction = direction.lower()
    next_room = G.current_room.exit(direction)
    G.enqueue_text(f"You proceed {direction}.")


@when("look")
def look():
    for text in G.generate_text():
        adventurelib.say(text)

    # TODO: What if a room's description needs to change dynamically, e.g. on
    # subsequent entrances?
    adventurelib.say(G.current_room.description)
