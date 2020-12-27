import functools
import random

import adventurelib
import zalgo_text

from engine.globals import G


_Z = zalgo_text.zalgo()
_Z.numAccentsUp = (1, 10)
_Z.numAccentsDown = (1, 10)
_Z.numAccentsMiddle = (1, 4)


_VOICES = [
    "HEEEHEHEHEHEHE",
    "THERE IS NO HOPE",
    "DID YOU HEAR THAT?",
    "I PROMISE YOU KNOWLEDGE",
]


def _y(x):
    """Shallow parabolic curve ensuring zalgo increases little at first.

    Then explodes.
    """
    return (5 / 900) * (x ** 2) + (4 / 9) * x


def _hear_voices(text, insanity):

    # TODO: Too much zalgo text! Decide letter-by-letter whether to zalgofy.
    _Z.zalgoChance = _y(insanity) / 100
    _Z.maxAccentsPerLetter = max(1, int(insanity / 10))

    # TODO: Condition number of breakpoints on length of text!
    num_breaks = int((insanity - 40) / 10)
    breakpoints = []
    if num_breaks > 0:
        breaks = [0]
        breaks.extend(sorted(random.sample(range(len(text)), min(num_breaks, len(text)))))
        breaks.append(len(text))
        breakpoints.extend(zip(breaks[:-1], breaks[1:]))
    else:
        breakpoints.append((0, len(text)))

    segments = []
    for i, (begin, end) in enumerate(breakpoints):
        if i > 0:
            segments.append(random.choice(_VOICES))
        segments.append(_Z.zalgofy(text[begin:end]))

    return "".join(segments)


def insayne(text, add_newline=True, insanity=None):
    """Renders @text to screen, modified based on player's insanity stat.

    Interpolates arcane markings and violent exhortations if player's sanity
    is not pristine. Renders UI text less and less legible as sanity degrades.
    """
    if add_newline:
        adventurelib.say("")
    if insanity is None:
        insanity = G.player.insanity.value
    text = _hear_voices(text, insanity)
    adventurelib.say(text)


sayne = functools.partial(insayne, insanity=0)
