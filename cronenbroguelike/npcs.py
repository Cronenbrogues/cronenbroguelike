from engine import actor
from engine import ai
from engine import event
from engine import item
from engine import say

from cronenbroguelike import book


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
    def fish_man_death_throes(fish_man):
        say.insayne(
            f"{fish_man.name} flops breathlessly upon the ground, blood "
            "commingling with piscine slobber. Half-formed gills flutter "
            "helplessly, urgently, then fall slack."
        )
        fish_man.alive = False

    monster.upon_death(fish_man_death_throes)
    monster.inventory.add(item.Item('ceremonial knife', 'knife', 'kris'))
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
        ai=ai.Librarian()
    )

    class _LibrarianEvent(event.Event):
        
        def execute(self):
            say.insayne(
                    "We all seek stillness of one sort or another. "
                    "You will find the way to stillness upon my body "
                    "when I die.")
            npc.die()
            self._will_execute = False 

    npc.ai.add_event(_LibrarianEvent())

    def librarian_death_throes(librarian):
        say.insayne(
            "The librarian grins impossibly wide. A thin rivulet of blood "
            "appears between his teeth. His eyes roll back and, with a giggle, "
            "he falls backward onto the ground as though reclining on a divan."
        )
        librarian.alive = False

    npc.upon_death(librarian_death_throes)
    npc.inventory.add(book.MeditationBook('meditation tome'))
    return npc
