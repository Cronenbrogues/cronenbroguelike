import random

from engine import actor
from engine import ai
from engine import dice
from engine import event
from engine.globals import G as _G
from engine import say

from cronenbroguelike import items
from cronenbroguelike import util


# TODO: I don't like doing this functionally. Use classes instead.
def fish_man():
    monster = actor.create_actor(
        health=10,
        psyche=10,
        strength=10,
        stamina=10,
        name="fish man",
        idle_text="There is a fish man slobbering in the corner.",
        ai=ai.HatesPlayer(),
    )
    monster.insanity.heal_or_harm(100)

    # TODO: Make a Monster class (or component) that encapsulates this behavior.
    # TODO: Store location as a member of Actors and Items. That way, monsters can
    # run away bleeding or something and die where they are, rather than being
    # presumed to die in the current room. Alternately, simply change how attacking
    # works when monsters are dead.
    #
    # TODO: Why isn't .alive = False working?
    def fish_man_death_throes(fish_man):
        say.insayne(
            f"{util.capitalized(fish_man.name)} flops breathlessly upon the "
            "ground, blood commingling with piscine slobber. Half-formed gills "
            "flutter helplessly, urgently, then fall slack."
        )

    monster.upon_death(fish_man_death_throes)
    monster.inventory.add(items.CeremonialKnife.create())
    return monster


def mad_librarian():
    npc = actor.create_actor(
        10,
        10,
        10,
        10,
        "mad librarian",
        "librarian",
        # TODO: How to deal with intro text? "The librarian leans in ..."
        idle_text="A mad librarian, clad in rags, hunches over a musty book.",
        ai=ai.Chill(),
    )
    npc.insanity.heal_or_harm(100)

    class _LibrarianEvent(event.Event):
        def execute(self):
            say.insayne(
                "Tittering and in a halted voice, the librarian utters these words:"
            )
            say.insayne("\"The flesh is active, yet it's only soothed")
            say.insayne(
                "when still. Through constant paradox, flesh moves.", add_newline=False
            )
            say.insayne("I hold stillness's secret! It is mine!", add_newline=False)
            say.insayne('Find it upon my body when I die."', add_newline=False)
            say.insayne(
                '"Now watch," cries the rag-clad wretch, "as the paradox '
                'is resolved."'
            )
            npc.die()
            self._will_execute = False

    npc.ai.add_event(_LibrarianEvent(), "talk")

    def librarian_death_throes(librarian):
        say.insayne(
            "The librarian grins impossibly wide. A thin rivulet of blood "
            "appears between his teeth. His eyes roll back and, with a giggle, "
            "he falls backward onto the ground as though reclining on a divan."
        )
        say.insayne("The edge of a hidebound book peeks from his rags.")

    npc.upon_death(librarian_death_throes)
    npc.inventory.add(items.MeditationBook.create())
    return npc


def smokes_man():
    npc = actor.create_actor(
        10,
        10,
        10,
        10,
        "smoker",
        "smokes man",
        "dude",
        "chill dude",
        "guy",
        idle_text=(
            "A smoker stands meditatively, cigarette in hand. "
            "He looks cool, maybe cooler than you."
        ),
        ai=ai.Chill(),
    )

    class _SmokesManEvent(event.Event):
        def execute(self):
            # TODO: Should not be G.player--what if somebody else wants a smoke?
            if _G.player.inventory.find("cigarette") or _G.player.inventory.find(
                "stub"
            ):
                say.insayne(
                    "The smoker clucks his tongue. \"You've already got a "
                    'smoke; why are you trying to bum one off me?"'
                )

            else:
                cigarette = random.choice(
                    [items.Cigarette, items.CigaretteStub]
                ).create()
                say.insayne(
                    '"Here you go," says the smoker between puffs. "Have a '
                    "smoke with me. It's all there is to do here, man. Just "
                    'that and wait to die and live again."'
                )
                _G.player.inventory.add(cigarette)
                lighter = npc.inventory.find("lighter")
                if lighter is not None:
                    say.insayne('"Here, you\'ll need this, too."')
                    npc.inventory.remove(lighter)
                    _G.player.inventory.add(lighter)
                    say.insayne('"No smoke without fire."')

    class _SmokesManSmokes(event.Event):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.owner = None
            self._timer = -1

        def execute(self):
            self._timer += 1
            if self._timer % 3 != 0:
                return
            roll = dice.roll("1d10")
            if roll <= 4:
                return
            cig = items.Cigarette.create()
            self.owner.inventory.add(cig)
            cig.consume(self.owner)

    npc.ai.add_event(_SmokesManEvent(), "talk")
    npc.ai.add_default_event(_SmokesManSmokes())

    def smoker_death_throes(smoker):
        say.insayne(
            'The smoker glances placidly around the environs. "Until the next '
            'time around, I guess." With a final nod, he breathes a perfect '
            "wreath of smoke, which dissipates solemnly."
        )

    npc.upon_death(smoker_death_throes)
    number_butts = random.choice(range(4, 7))
    for _ in range(number_butts):
        npc.inventory.add(items.CigaretteButt.create())
    npc.inventory.add(items.CigaretteStub.create())
    npc.inventory.add(items.CigaretteStub.create())
    npc.inventory.add(items.Cigarette.create())
    npc.inventory.add(items.Lighter.create())

    return npc
