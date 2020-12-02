import re

import adventurelib

from engine import dice
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

    # TODO: Bespoke descriptions for all items and characters.
    for item in G.current_room.items:
        G.enqueue_text(f'There is a(n) {item.name} lying on the ground.')
    for character in G.current_room.characters:
        G.enqueue_text(f'There is a(n) {character.name} slobbering in the corner.')
    G.enqueue_text(f'Exits are {", ".join(G.current_room.exits)}.')

    for i, text in enumerate(G.generate_text()):
        if i > 0:
            adventurelib.say("")
        say.insayne(text)


@adventurelib.when("stats")
def stats():
    name_str = f'{G.player.name}'
    say.insayne(name_str)
    # TODO: Unfuck this for zalgo.
    say.insayne(''.join('-' for _ in name_str))
    for stat in G.player.all_stats():
        if hasattr(stat, 'current_value'):
            say.insayne(f"{stat.name:10}: {stat.current_value}/{stat.value}")
        else:
            say.insayne(f"{stat.name:10}: {stat.value}")


@adventurelib.when("cheat CODE")
def cheat(code):
    m = re.search(r"([a-zA-Z]+)\s+(\-?\d+)", code)
    if m is None:
        return

    stat, delta = m.groups()
    stat = stat.lower()
    delta = int(delta)
    getattr(G.player, stat).modify(delta)
    adventurelib.say(
        f"{stat.title()} {'in' if delta >= 0 else 'de'}creased by {delta}."
    )


def _resolve_attack(attacker, defender):
    # TODO: Add equipment, different damage dice, etc.
    is_player = attacker is G.player
    if is_player:
        subj, obj = ['you', defender.name]
    else:
        subj, obj = [attacker.name, 'you']
    miss = 'miss' if is_player else 'misses'
    hit = 'hit' if is_player else 'hits'

    strength_mod = int((attacker.strength.value - 10) / 2)
    to_hit = strength_mod + dice.roll('1d20')
    if to_hit < (10 + (defender.stamina.value - 10) / 2):
        say.insayne(f'{subj.title()} {miss}.')

    else:
        damage = dice.roll('1d8') + strength_mod
        # TODO: How to organize messages better? Death also creates text, so
        # there should be a way to make sure the messages are ordered.
        say.insayne(f'{subj.title()} {hit} for {damage} damage!')
        defender.health.heal_or_harm(-1 * damage)


def _get_opponent(actor_name):
    return G.current_room.characters.find(actor_name)


@adventurelib.when("attack ACTOR")
def attack(actor):
    actor_name = actor  # Variable names are constrained by adventurelib.
    # TODO: Consider turn order--some kind of agility stat?
    # TODO: Other combat actions--spells, items, fleeing, etc.
    # TODO: Affinity/factions so monsters can choose whom to strike.
    defender = _get_opponent(actor_name)
    if defender is None:
        say.insayne(f'There is no {actor_name} here.')
        return

    _resolve_attack(G.player, defender)
    for actor in G.current_room.characters:
        assert actor.ai is not None
        defender = actor.ai.choose_target(G.current_room)
        _resolve_attack(actor, defender)
