import random

from engine import actor
from engine import ai
from engine import event
from engine.globals import G as _G
from engine import say

from cronenbroguelike import items


# TODO: I don't like doing this functionally. Use classes instead.
def fish_man():
    monster = actor.create_actor(
        health=10,
        psyche=10,
        strength=10,
        stamina=10,
        will=10,
        wisdom=10,
        insanity=100,
        name="Fish Man",
        ai=ai.HatesPlayer(),
    )

    # TODO: Make a Monster class (or component) that encapsulates this behavior.
    # TODO: Store location as a member of Actors and Items. That way, monsters can
    # run away bleeding or something and die where they are, rather than being
    # presumed to die in the current room. Alternately, simply change how attacking
    # works when monsters are dead.
    #
    # TODO: Why isn't .alive = False working?
    def fish_man_death_throes(fishman):
        say.insayne(
            f"{fishman.name} flops breathlessly upon the ground, blood "
            "commingling with piscine slobber. Half-formed gills flutter "
            "helplessly, urgently, then fall slack."
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
        10,
        10,
        100,
        "mad librarian",
        "librarian",
        # TODO: How to deal with intro text? "The librarian leans in ..."
        ai=ai.Chill(),
    )

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

    npc.ai.add_event(_LibrarianEvent())

    def librarian_death_throes(librarian):
        say.insayne(
            "The librarian grins impossibly wide. A thin rivulet of blood "
            "appears between his teeth. His eyes roll back and, with a giggle, "
            "he falls backward onto the ground as though reclining on a divan."
        )

    npc.upon_death(librarian_death_throes)
    npc.inventory.add(items.MeditationBook.create())
    return npc


def smokes_man():
    npc = actor.create_actor(
        10,
        10,
        10,
        10,
        10,
        10,
        100,
        "smoker",
        "dude",
        "chill dude",
        "guy",
        ai=ai.Chill(),
    )

    class _SmokesManEvent(event.Event):
        def execute(self):
            # TODO: Should not be G.player--what if somebody else wants a smoke?
            if _G.player.inventory.find("smoke"):
                say.insayne(
                    "The smoker clucks his tongue. \"You've already got a "
                    "smoke; why are you trying to bum one off me?"
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
                say.insayne(f"You acquire a {cigarette.name}.")

    npc.ai.add_event(_SmokesManEvent())

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

    return npc
