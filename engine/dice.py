import random
import re


_DICE_RE = re.compile(r"^(\d*)d(\d+)$")


def _roll_die(faces):
    return random.randint(1, faces)


def roll(dice_expression):
    match = _DICE_RE.search(dice_expression)
    if match is None:
        # TODO: Bespoke exception type.
        raise Exception
    number_dice, die_type = match.groups()
    if not number_dice:
        number_dice = 1
    else:
        number_dice = int(number_dice)
    die_type = int(die_type)
    return sum([_roll_die(die_type) for _ in range(number_dice)])
