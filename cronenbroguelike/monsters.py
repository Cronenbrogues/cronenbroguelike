from engine import actor
from engine import ai
from engine import item
from engine import say


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
