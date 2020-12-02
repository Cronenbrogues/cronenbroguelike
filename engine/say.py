import random

import adventurelib
import zalgo_text

from engine.globals import G


_Z = zalgo_text.zalgo()


_VOICES = [
    "HEEEHEHEHEHEHE",
    "THERE IS NO HOPE",
    "DID YOU HEAR THAT?",
    "I PROMISE YOU KNOWLEDGE",
]


def insayne(text):
    """Renders @text to screen, modified based on player's insanity stat.

    Interpolates arcane markings and violent exhortations if player's sanity
    is not pristine. Renders UI text less and less legible as sanity degrades.
    """
    if G.player.insanity.value < 30:
        adventurelib.say(text)
        return

    # TODO: Too much zalgo text! Decide letter-by-letter whether to zalgofy.
    _Z.maxAccentsPerLetter = max(0, int((G.player.insanity.value - 20) / 10))

    # TODO: Condition breakpoints on length of text!
    num_breaks = int((G.player.insanity.value - 40) / 10)
    breakpoints = []
    if num_breaks > 0:
        breaks = [0]
        breaks.extend(sorted(random.sample(range(len(text)), num_breaks)))
        breaks.append(len(text))
        breakpoints.extend(zip(breaks[:-1], breaks[1:]))
    else:
        breakpoints.append((0, len(text)))

    segments = []
    for i, (begin, end) in enumerate(breakpoints):
        if i > 0:
            segments.append(random.choice(_VOICES))
        segments.append(_Z.zalgofy(text[begin:end]))

    adventurelib.say("".join(segments))
