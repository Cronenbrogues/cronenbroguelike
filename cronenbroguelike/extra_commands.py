import random
import re

import adventurelib

from cronenbroguelike import commands
from engine.globals import G
from engine import say


###
# Synonyms for some of the basic commands.
###


@adventurelib.when("consume ITEM", verb="consume")
@adventurelib.when("eat ITEM", verb="eat")
@adventurelib.when("smoke ITEM", verb="smoke")
def consume(item, verb):
    commands.use(item, verb)


@adventurelib.when("exit DIRECTION")
@adventurelib.when("proceed DIRECTION")
def proceed(direction):
    commands.go(direction)


@adventurelib.when("sit there and starve")
@adventurelib.when("commit suicide")
@adventurelib.when("die")
@adventurelib.when("just die")
@adventurelib.when("hold breath forever")
def die():
    commands.suicide()


###
# Cheat codes! These will actually become essential to the game.
###


class _CheatException(Exception):
    pass


_STAT_PATTERN = re.compile(r"(\w+)\s+(\-?\d+)")


def _cheat_stat(stat, delta):
    stat = stat.lower()
    delta = int(delta)
    if stat == "heal":
        G.player.health.heal_or_harm(delta, cause="CHEATING")
    else:
        try:
            the_stat = getattr(G.player, stat)
        except:
            raise _CheatException
        else:
            the_stat.modify(delta)


_ABILITY_PATTERN = re.compile(r"add ability (\w+)")


def _cheat_ability(ability_name):
    from cronenbroguelike import ability

    try:
        to_add = getattr(ability, ability_name)
    except AttributeError:
        raise _CheatException
    else:
        G.player.add_ability(to_add())


@adventurelib.when("cheat CODE")
def cheat(code):
    # TODO: Make healing more general.
    matches = []
    match = _STAT_PATTERN.search(code)
    if match is not None:
        matches.append((_cheat_stat, match))

    match = _ABILITY_PATTERN.search(code)
    if match is not None:
        matches.append((_cheat_ability, match))

    for function, match in matches:
        try:
            function(*match.groups())
            break
        except _CheatException:
            pass

    else:
        say.insayne(
            "You attempt to pry open cosmic mysteries but fail. Your "
            "pitiful mind reels with the effort."
        )
        G.player.insanity.heal_or_harm(15)


###
# Commands for testing.
###


@adventurelib.when("random")
def random_action():
    skip = ['?', 'help', 'quit', 'random', 'suicide',
            'north', 'south', 'east', 'west']
    filtered_commands = [c for c in adventurelib.commands if " ".join(c[0].prefix) not in skip]
    random_command = random.choice(filtered_commands)
    command_pattern = random_command[0]

    entity_names = (
        [npc.name for npc in G.player.current_room.npcs] +
        [corpse.name for corpse in G.player.current_room.corpses] +
        [item.name for item in G.player.inventory] +
        [item.name for item in G.player.current_room.items] +
        list(G.player.current_room._exits)
    )

    args = [random.choice(entity_names) for i in range(len(command_pattern.argnames))]
    final_command = f"{' '.join(command_pattern.prefix)} {' '.join(args)}"
    say.insayne(f"random command: {final_command}", insanity=0)

    # Pass through adventurelib rather than calling directly to avoid some
    # complexity with multiple-argument commands, like loot.
    adventurelib._handle_command(final_command)
