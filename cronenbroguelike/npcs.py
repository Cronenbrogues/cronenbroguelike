import random

from engine import actor
from engine import ai
from engine import dice
from engine import event
from engine.globals import G as _G
from engine import say
from engine import when

from . import extra_description

from cronenbroguelike import items
from cronenbroguelike import util


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
        name="fish man",
        idle_text="There is a fish man slobbering in the corner.",
        ai=ai.HatesPlayer(),
    )

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
        10,
        10,
        100,
        "mad librarian",
        "librarian",
        # TODO: How to deal with intro text? "The librarian leans in ..."
        idle_text="A mad librarian, clad in rags, hunches over a musty book.",
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
            say.insayne("Find it upon my body when I die.\"", add_newline=False)
            say.insayne(
                    "\"Now watch,\" cries the rag-clad wretch, \"as the paradox "
                    "is resolved.\"")
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
        10,
        10,
        100,
        "smoker",
        "smokes man",
        "dude",
        "chill dude",
        "guy",
        idle_text=(
                "A smoker stands meditatively, cigarette in hand. "
                "He looks cool, maybe cooler than you."),
        ai=ai.Chill(),
    )

    class _SmokesManEvent(event.Event):

        def execute(self):
            # TODO: Should not be G.player--what if somebody else wants a smoke?
            if _G.player.inventory.find("cigarette") or _G.player.inventory.find("stub"):
                say.insayne(
                        'The smoker clucks his tongue. "You\'ve already got a '
                        'smoke; why are you trying to bum one off me?"')

            else:
                cigarette = random.choice(
                        [items.Cigarette, items.CigaretteStub]).create()
                say.insayne(
                    '"Here you go," says the smoker between puffs. "Have a '
                    'smoke with me. It\'s all there is to do here, man. Just '
                    'that and wait to die and live again."')
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
            roll = dice.roll('1d10')
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
            'wreath of smoke, which dissipates solemnly.'
        )

    npc.upon_death(smoker_death_throes)
    number_butts = random.choice(range(4, 7))
    for _ in range(number_butts):  # add myriad butts
        npc.inventory.add(items.CigaretteButt.create())
    npc.inventory.add(items.CigaretteStub.create())
    npc.inventory.add(items.CigaretteStub.create())
    npc.inventory.add(items.Cigarette.create())
    npc.inventory.add(items.Lighter.create())

    return npc


def office_computer():
    npc = actor.create_actor(
        1000,
        10,
        1000,  # strength
        10,
        10,
        10,
        100,
        "your computer",
        "computer",
        idle_text="Your computer hums gently on your desk.",
        ai=ai.Chill(),
    )

    def use_computer(consumer):
        insanity = _G.player.insanity.value
        desc = extra_description.get_interval(insanity, extra_description.use_computer_descriptions)
        say.insayne(desc)
        if insanity >= 10 and insanity < 20:
            _G.player.insanity.modify(2)
        elif insanity >= 25:
            _G.player.health.heal_or_harm(-10)

    class _ComputerTick(event.Event):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def execute(self):
            insanity = _G.player.insanity.value
            desc = extra_description.get_interval(insanity, extra_description.office_computer_descriptions)
            npc.idle_text = desc

    def computer_death_throes(actor):
        say.insayne("The computer falls to pieces.")

    _G.add_event(_ComputerTick(), "pre")
    npc.upon_death(computer_death_throes)

    npc.consume = use_computer

    return npc


def coffee_machine():
    npc = actor.create_actor(
        10,
        10,
        10,  # strength
        10,
        10,
        10,
        100,
        "coffee machine",
        idle_text="A coffee machine gurgles pleasantly on the counter.",
        ai=ai.Chill(),
    )

    # npc.ai.add_event(_SmokesManEvent(), "talk")
    # npc.ai.add_default_event(_ComputerGetsMad())

    def coffee_machine_death_throes(librarian):
        say.insayne(
            "The librarian grins impossibly wide. A thin rivulet of blood "
            "appears between his teeth. His eyes roll back and, with a giggle, "
            "he falls backward onto the ground as though reclining on a divan."
        )
        say.insayne("The edge of a hidebound book peeks from his rags.")

    npc.upon_death(coffee_machine_death_throes)
    # npc.inventory.add(items.MeditationBook.create())

    def use_coffee_machine(consumer):
        # say.insayne("using coffee machine")
        # TODO: add text?
        _G.player.inventory.add(items.Coffee.create())

    class _CoffeeMachineTick(event.Event):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def execute(self):
            insanity = _G.player.insanity.value
            desc = extra_description.get_interval(insanity, extra_description.coffee_machine_descriptions)
            npc.idle_text = desc

    _G.add_event(_CoffeeMachineTick(), "pre")
    npc.consume = use_coffee_machine

    return npc


def office_copier():
    npc = actor.create_actor(
        1000,
        10,
        10,  # strength
        10,
        10,
        10,
        100,
        "copier",
        idle_text="The office's byzantine copier looks to be broken again.",
        ai=ai.Chill(),
    )

    def use_office_copier(consumer):
        insanity = _G.player.insanity.value
        if insanity < 20:
            say.insayne("The copier seems to be broken, as usual.")
        elif insanity < 29:
            bodyparts = ["fingers", "tongues", "arms", "lips", "nipples"]
            say.insayne("The copier moans lasciviously. You feel its hot breath on your neck. It envelops you, and penetrates you.")
            say.insayne("Abruptly, orgasmically, new "
                        f"{random.choice(bodyparts)} erupt from your skin.")
            _G.player.insanity.modify(3)
        else:
            say.insayne("The copier sighs.")
            say.insayne("You hear a meaty thumping coming from the direction of the meeting room.")

    class _CopierTick(event.Event):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def execute(self):
            insanity = _G.player.insanity.value
            desc = extra_description.get_interval(insanity, extra_description.copier_descriptions)
            npc.idle_text = desc

    def office_copier_death_throes(actor):
        pass

    _G.add_event(_CopierTick(), "pre")
    npc.upon_death(office_copier_death_throes)
    npc.consume = use_office_copier

    return npc


def gary():
    npc = actor.create_actor(
        1000,
        10,
        1000,
        10,
        10,
        10,
        100,
        "gary",
        ai=ai.Chill(),
    )

    class _GaryJoke(event.Event):

        def execute(self):
            insanity = _G.player.insanity.value
            jokes = extra_description.get_interval(insanity, extra_description.gary_jokes)
            if insanity <= 10:
                say.insayne("Gary starts to tell a joke...")
            elif insanity <= 20:
                say.insayne("Gary sneers...")
            for line in random.choice(jokes).split("\n"):
                say.insayne(line)
            if insanity < 10:
                say.insayne("You groan.")
                _G.player.insanity.modify(2)
            elif insanity <= 20:
                say.insayne("You try not to make eye contact.")
                say.insayned("Gary laughs uproariously, spittle flying all over you.")

    class _GaryHit(event.Event):

        def execute(self):
            insanity = _G.player.insanity.value
            if insanity >= 20:
                say.insayne("Gary smiles.")
                say.insayne('"I\'ve been waiting so long for this..."')
                npc.ai = ai.HatesPlayer()
            else:
                say.insayne('"Ow!"')

    class _GaryTick(event.Event):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def execute(self):
            insanity = _G.player.insanity.value
            desc = extra_description.get_interval(insanity, extra_description.gary_descriptions)
            npc.idle_text = desc

    def gary_death_throes(actor):
        pass

    npc.ai.add_event(_GaryJoke(), "talk")
    npc.ai.add_event(_GaryHit(), "attack")
    _G.add_event(_GaryTick(), "pre")
    npc.upon_death(gary_death_throes)

    return npc


def writhing_office_mass():
    npc = actor.create_actor(
        1000,
        10,
        1000,
        10,
        10,
        10,
        100,
        "writhing mass",
        "mass",
        ai=ai.Chill(),
    )

    class _WrithingMassTalk(event.Event):

        def execute(self):
            say.insayne('The writhing mass speaks, many voices merging into one:')
            say.insayne('"Hey champ! How are those quarterly targets coming along? Working hard or hardly working?"')
            say.insayne('The writhing mass cackles.')
            say.insayne('"You should go see Gary! Now there\'s a team player. Maybe do him a favor! Lord knows he\'s done enough for you..."')
            insanity = _G.player.insanity.value
            if insanity == 29:
                _G.player.insanity.modify(1)

    class _WrithingMassHit(event.Event):

        def execute(self):
            say.insayne('"LOVE the chutzpah, bud! But it\'s futile. Believe us, we\'ve tried! Over, and over, and over...."')

    def writhing_mass_death_throes(actor):
        pass

    npc.ai.add_event(_WrithingMassTalk(), "talk")
    npc.ai.add_event(_WrithingMassHit(), "attack")
    npc.upon_death(writhing_mass_death_throes)
    npc.idle_text = "The mass of bodies writhes expectantly."

    return npc
