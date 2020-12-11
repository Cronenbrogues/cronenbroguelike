import adventurelib

from engine.globals import G
from engine import item
from engine import say


class _Statistic:

    _MIN_VALUE = None
    _MAX_VALUE = None

    def __init__(self, value, owner=None):
        self._value = value
        # TODO: Rethink this; it's an indication of poor design.
        self._owner = owner

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, new_owner):
        self._owner = new_owner

    def modify(self, delta):
        # TODO: Maybe all this nonsense with a latent value that is between
        # _MIN and _MAX is overkill.
        old_value = self.value
        self._value += delta

        # This line singlehandedly eliminates the nonsense but in a tortuous
        # fashion.
        self._value = self.value
        new_value = self.value
        delta = new_value - old_value
        if self.owner.log_stats:
            if delta:
                message = f"{'in' if delta >= 0 else 'de'}creased by {abs(delta)}"
            else:
                message = "does not change"
            say.sayne(f"{self._NAME.title()} {message}.")

    @property
    def value(self):
        surface_value = self._value
        if self._MIN_VALUE is not None:
            surface_value = max(self._MIN_VALUE, surface_value)
        if self._MAX_VALUE is not None:
            surface_value = min(self._MAX_VALUE, surface_value)
        return surface_value

    @property
    def name(self):
        return self._NAME


class _VariableStatistic(_Statistic):
    def __init__(self, value):
        self._value = value
        self._current_value = value
        self._last_cause = None

    @property
    def current_value(self):
        return self._current_value

    def heal_or_harm(self, delta, cause=None):
        self._last_cause = None
        # TODO: This logic is crazy. Just do away with all the min/max value
        # stuff.
        surface_value = self._value
        if self._MIN_VALUE is not None:
            surface_value = max(self._MIN_VALUE, surface_value)
        if self._MAX_VALUE is not None:
            surface_value = min(self._MAX_VALUE, surface_value)
        old_value = self._current_value
        self._current_value += delta
        self._current_value = min(self._current_value, self._value)
        new_value = self._current_value
        delta = new_value - old_value
        if self.owner.log_stats:
            say.sayne(
                f"{self._NAME.title()} "
                f"{'restored' if delta >= 0 else 'damaged'} by {abs(delta)}."
            )


class Health(_VariableStatistic):
    _NAME = "health"

    def heal_or_harm(self, delta, cause=None):
        super().heal_or_harm(delta, cause)
        if self._current_value <= 0:
            self._owner.die(cause=cause)


class Psyche(_VariableStatistic):
    _NAME = "psyche"


class _BaseStatistic(_Statistic):
    # This is a really weird way to do things. _Statistic is not currently
    # an abstract class but should be. Maybe statistics don't need to be
    # this complicated.
    # Also, what if I want to make Strength variable but not display that in
    # the `stats` command?
    _MIN_VALUE = 0
    _MAX_VALUE = 30


class Strength(_BaseStatistic):
    _NAME = "strength"


class Stamina(_BaseStatistic):
    _NAME = "stamina"


class Will(_BaseStatistic):
    _NAME = "will"


class Wisdom(_BaseStatistic):
    _NAME = "wisdom"


class Insanity(_Statistic):
    _MIN_VALUE = 0
    _MAX_VALUE = 100
    _NAME = "insanity"


# TODO: Make a Player class whose death ends (or restarts) the game.
# TODO: If any other Actor dies, there should be an `alive` flag to reflect
# that. Actors that are not alive should be removed from the room's
# _characters bag and added to the _items bag (or otherwise prevented from
# attacking, maybe with a separate bag for corpses?).
class Actor:

    _CANONICAL_STAT_ORDER = [
        "health",
        "psyche",
        "strength",
        "stamina",
        "will",
        "wisdom",
        "insanity",
    ]

    def __init__(self, actor_item, *statistics, **kwargs):
        self._actor_item = actor_item
        self._statistics = {}
        for statistic in statistics:
            self._statistics[statistic.name] = statistic
            statistic.owner = self
        self._ai = kwargs.pop("ai", None)
        self._death_throes = lambda this: None
        self._inventory = adventurelib.Bag()
        self._read_books = set()
        self._abilities = {}

        self.alive = True
        self.log_stats = False

    @property
    def ai(self):
        return self._ai

    @property
    def inventory(self):
        return self._inventory

    @property
    def abilities(self):
        return self._abilities

    def add_ability(self, ability):
        # TODO: "You" vs. name problem as always.
        say.insayne(f"You gain the ability {ability.NAME}.")
        # TODO: Bidirectional reference problem as always.
        ability.owner = self
        self._abilities[ability.NAME] = ability

    def has_read(self, book):
        return book.name in self._read_books

    def set_has_read(self, book):
        self._read_books.add(book.name)

    # TODO: This sucks; using __getattr__ or something might help. Maybe just
    # hard-code the stats that all actors have? Dynamically add properties?
    # ... use metaclasses?
    def get_stat(self, stat_name):
        stat = self._statistics.get(stat_name)
        if stat is not None:
            return stat
        raise AttributeError

    def __getattr__(self, stat_name):
        # TODO: This is weird. Maybe just inherit from Item.
        try:
            return getattr(self._actor_item, stat_name)
        except AttributeError:
            return self.get_stat(stat_name)

    def all_stats(self):
        """Returns stat names and values in a reasonable order."""
        # TODO: There's got to be a better way to do this.
        stat_order = self._CANONICAL_STAT_ORDER + sorted(
            self._statistics.keys() - set(self._CANONICAL_STAT_ORDER)
        )
        return [self._statistics[stat_name] for stat_name in stat_order]

    def die(self, cause=None):
        if self is G.player:
            G.cause_of_death = cause
            say.insayne("You die.")
            say.insayne("...")
        self._death_throes(self)

    def upon_death(self, callback):
        self._death_throes = callback


# TODO: Make this a classmethod of Actor.
def create_actor(
    health, psyche, strength, stamina, will, wisdom, insanity, name, *aliases, **kwargs
):
    """Convenience function to create actors with canonical stats."""
    actor_item = item.Item(name, *aliases)
    return Actor(
        actor_item,
        Health(health),
        Psyche(psyche),
        Strength(strength),
        Stamina(stamina),
        Will(will),
        Wisdom(wisdom),
        Insanity(insanity),
        **kwargs,
    )
