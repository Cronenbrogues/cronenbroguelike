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
    # TODO: Fix a(n) problems throughout code base.
    for item in G.current_room.items:
        G.enqueue_text(f'There is a(n) {item.name} lying on the ground.')
    for character in G.current_room.characters:
        # TODO: Move these descriptions to the actor.
        if character.alive:
            G.enqueue_text(
                    f'There is a(n) {character.name} slobbering in the corner.')
        else:
            G.enqueue_text(
                    f'The corpse of a(n) {character.name} molders here.')
    G.enqueue_text(f'Exits are {", ".join(G.current_room.exits)}.')

    for i, text in enumerate(G.generate_text()):
        say.insayne(text)


@adventurelib.when("stats")
def stats():
    lines = []
    name_str = f'{G.player.name}'
    lines.append(name_str)
    # TODO: Unfuck this for zalgo.
    lines.append(''.join('-' for _ in name_str))
    for stat in G.player.all_stats():
        if hasattr(stat, 'current_value'):
            lines.append(f"{stat.name:10}: {stat.current_value}/{stat.value}")
        else:
            lines.append(f"{stat.name:10}: {stat.value}")

    for i, line in enumerate(lines):
        add_newline = (i == 0)
        say.insayne(line, add_newline=add_newline)



@adventurelib.when("cheat CODE")
def cheat(code):
    # TODO: Make healing more general.
    m = re.search(r"([a-zA-Z]+)\s+(\-?\d+)", code)
    if m is None:
        return

    stat, delta = m.groups()
    stat = stat.lower()
    delta = int(delta)
    if stat == 'heal':
        G.player.health.heal_or_harm(delta)
        stat_str = 'health'
    else:
        getattr(G.player, stat).modify(delta)
        stat_str = stat.title()
    say.sayne(
        f"{stat_str} {'in' if delta >= 0 else 'de'}creased by {delta}."
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
    # TODO: Other actions should be considered "combat" actions. Implement some
    # notion of turns.
    # TODO: Other combat actions--spells, items, fleeing, etc.
    # TODO: Affinity/factions so monsters can choose whom to strike.
    defender = _get_opponent(actor_name)
    if defender is None:
        say.insayne(f'There is no {actor_name} here.')
        return

    if not defender.alive:
        say.insayne(
                f"In a blind fury, you hack uselessly at the {actor_name}'s "
                "corpse.")
        # TODO: Log in the statistic setter instead of here.
        # TODO: Really, seriously fix the newline issue.
        G.player.insanity.modify(10)
        say.insayne("Your insanity increases by 10.")
        return

    _resolve_attack(G.player, defender)
    for character in G.current_room.characters:
        if not character.alive:
            continue
        assert character.ai is not None
        defender = character.ai.choose_target(G.current_room)
        _resolve_attack(character, defender)
