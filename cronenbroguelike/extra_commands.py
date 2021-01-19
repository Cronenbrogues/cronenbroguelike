import re

import adventurelib

from cronenbroguelike import commands
from engine.globals import G


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
