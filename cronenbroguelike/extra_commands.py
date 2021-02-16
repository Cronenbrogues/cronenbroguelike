import logging
import random
import re

from cronenbroguelike import commands
from whimsylib.globals import G
from whimsylib import say
from whimsylib import when


###
# Synonyms for some of the basic commands.
###


@when.when("consume ITEM", verb="consume")
@when.when("eat ITEM", verb="eat")
@when.when("smoke ITEM", verb="smoke")
def consume(item, verb):
    commands.use(item, verb)


@when.when("exit DIRECTION")
@when.when("proceed DIRECTION")
def proceed(direction):
    commands.go(direction)


@when.when("sit there and starve")
@when.when("commit suicide")
@when.when("die")
@when.when("just die")
@when.when("hold breath forever")
def die():
    commands.suicide()


###
# Cheat codes! These will actually become essential to the game.
###


class _CheatException(Exception):
    pass


def _get_stat(actor, stat_name):
    try:
        return getattr(actor, stat_name)
    except AttributeError:
        raise _CheatException


def _modify_stat(stat, delta):
    stat = stat.strip().lower()
    try:
        delta = int(delta)
    except ValueError:
        raise _CheatException
    stat = _get_stat(G.player, stat)
    stat.modify(delta)


def _heal_stat(stat, delta):
    if not stat:
        stat = "health"
    stat = stat.strip().lower()
    try:
        delta = int(delta)
    except ValueError:
        raise _CheatException
    stat = _get_stat(G.player, stat)
    if hasattr(stat, "heal_or_harm"):
        stat.heal_or_harm(delta)
    else:
        raise _CheatException


_HEAL_PATTERN = re.compile(r"^\s*heal\s+(?:(\w+)\s+)?(\-?\d+)\s*$", re.IGNORECASE)


_STAT_PATTERN = re.compile(r"^\s*(\w+)\s+(\-?\d+)\s*$")


_ABILITY_PATTERN = re.compile(r"^\s*add\s+ability\s+(\w+)\s*$", re.IGNORECASE)


def _cheat_ability(ability_name):
    from cronenbroguelike import ability

    try:
        to_add = getattr(ability, ability_name)
    except AttributeError:
        raise _CheatException
    else:
        G.player.add_ability(to_add())


@when.when("cheat CODE")
def cheat(code):
    # TODO: Make healing more general.
    matches = []

    for pattern, function in [
        (_HEAL_PATTERN, _heal_stat),
        (_STAT_PATTERN, _modify_stat),
        (_ABILITY_PATTERN, _cheat_ability),
    ]:
        match = pattern.search(code)
        if match is not None:
            matches.append((function, match))
            break

    for function, match in matches:
        logging.debug(f"function is {function}")
        logging.debug(f"match.groups is {match.groups()}")
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


@when.when("random")
def random_action():
    skip = [
        "?",
        "help",
        "quit",
        "random",
        "suicide",
        "north",
        "south",
        "east",
        "west",
        None,
    ]
    filtered_commands = [
        c for c in when.CommandHandler.COMMANDS if c[0].prefix not in skip
    ]

    random_command = random.choice(filtered_commands)
    command_pattern = random_command[0]

    entity_names = (
        [npc.name for npc in G.player.current_room.npcs]
        + [corpse.name for corpse in G.player.current_room.corpses]
        + [item.name for item in G.player.inventory]
        + [item.name for item in G.player.current_room.items]
        + list(G.player.current_room._exits)
    )

    args = [random.choice(entity_names) for i in range(len(command_pattern.arguments))]
    final_command = f"{' '.join(command_pattern.prefix)} {' '.join(args)}"
    say.insayne(f"random command: {final_command}", insanity=0)

    when.handle(final_command)
