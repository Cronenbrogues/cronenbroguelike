import adventurelib

from engine import bag
from engine.globals import G
from engine import item
from engine import say
from engine import tartarus
from cronenbroguelike import util


class _Statistic:

    _NAME = None
    _MINIMUM_VALUE = 0

    def __init__(self, value, owner=None):
        self.owner = owner  # Fully modifiable data member.
        self._static_value = value

    def _log_modify(self, delta):
        if delta:
            message = f"{'in' if delta >= 0 else 'de'}creased by {abs(delta)}"
        else:
            message = "does not change"
        say.insayne(f"{util.capitalized(self._NAME)} {message}.")

    def _modify(self, delta, do_log=True):
        self._static_value += delta
        self._static_value = max(self._MINIMUM_VALUE, self._static_value)
        if self.owner.log_stats and do_log:
            self._log_modify(delta)

    def modify(self, delta, **kwargs):
        return NotImplemented

    @property
    def name(self):
        return self._NAME


class _StaticStatistic(_Statistic):

    _NAME = None

    def __init_subclass__(cls):
        if cls._NAME is None:
            cls._NAME = cls.__name__.lower()

    def modify(self, delta, **kwargs):
        self._modify(delta, **kwargs)

    @property
    def value(self):
        return self._static_value


class _VariableStatistic(_Statistic):

    _NAME = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._variable_value = self._default_value
        self.last_cause = None  # Fully modifiable.

    def __init_subclass__(cls):
        if cls._NAME is None:
            cls._NAME = cls.__name__.lower()

    @property
    def maximum(self):
        return self._static_value

    @property
    def value(self):
        return self._variable_value

    @property
    def _default_value(self):
        return self._static_value

    def _log_current(self, delta):
        say.insayne(
            f"{util.capitalized(self._NAME)} "
            f"{'restored' if delta >= 0 else 'damaged'} by {abs(delta)}."
        )

    def modify(self, delta, cause=None, do_log=True):
        old_value = self.maximum
        cause = self.last_cause or cause
        self._modify(delta, do_log)
        actual_delta = self.maximum - old_value
        self.heal_or_harm(actual_delta, cause, do_log=False)

    def heal_or_harm(self, delta, cause=None, do_log=True):
        self.last_cause = cause
        self._variable_value += delta
        self._variable_value = min(self.maximum, self._variable_value)
        self._variable_value = max(self._MINIMUM_VALUE, self._variable_value)
        if self.owner.log_stats and do_log:
            self._log_current(delta)


class Health(_VariableStatistic):
    def heal_or_harm(self, *args, **kwargs):
        super().heal_or_harm(*args, **kwargs)
        if self.value <= 0:
            self.owner.die(cause=self.last_cause)


class Psyche(_VariableStatistic):
    pass


class Insanity(_VariableStatistic):
    @property
    def _default_value(self):
        return self._MINIMUM_VALUE

    def _log_current(self, delta):
        say.insayne(
            f"{util.capitalized(self._NAME)} "
            f"{'increased' if delta >= 0 else 'assuaged'} by {abs(delta)}."
        )


class Strength(_StaticStatistic):
    pass


class Stamina(_StaticStatistic):
    pass


# TODO: Make a Player class whose death ends (or restarts) the game.
# TODO: If any other Actor dies, there should be an `alive` flag to reflect
# that. Actors that are not alive should be removed from the room's
# _characters bag and added to the _items bag (or otherwise prevented from
# attacking, maybe with a separate bag for corpses?).
class Actor:

    _CANONICAL_STAT_ORDER = [
        "health",
        "psyche",
        "insanity",
        "strength",
        "stamina",
    ]

    def __init__(self, actor_item, *statistics, **kwargs):
        # Many of these private methods will be swappable if body-swapping is
        # implemented, e.g. mental stats, abilities, idle_text, ai ...
        self._actor_item = actor_item
        self._statistics = {}
        for statistic in statistics:
            self._statistics[statistic.name] = statistic
            statistic.owner = self
        self._ai = kwargs.pop("ai", None)
        if self._ai is not None:
            self._ai.owner = self
        self._idle_text = kwargs.pop("idle_text", None)
        self._death_throes = lambda this: None
        self._inventory = bag.Bag()
        self._read_books = set()
        self._abilities = {}

        # Assignable data members.
        self.current_room = None
        self.alive = True
        self.log_stats = False

    @property
    def ai(self):
        return self._ai

    @property
    def inventory(self):
        # TODO: Would be good if player's inventory always alerted when an item
        # was gained/lost.
        return self._inventory

    @property
    def abilities(self):
        return self._abilities

    @property
    def idle_text(self):
        return self._idle_text

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
    # TODO: How does this change when equipment is added?
    # TODO: How does this change when body-swapping is added?
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
            cause = cause or self.health.last_cause
            G.cause_of_death = cause
            say.insayne("You die.")
            say.insayne("...")
            raise tartarus.RaptureException("")
        else:
            self.alive = False
            self._death_throes(self)
            self.current_room.characters.remove(self)
            self.current_room.corpses.add(self)

    def upon_death(self, callback):
        self._death_throes = callback


# TODO: Make this a classmethod of Actor.
def create_actor(health, psyche, strength, stamina, name, *aliases, **kwargs):
    """Convenience function to create actors with canonical stats."""
    actor_item = item.Item(name, *aliases)
    return Actor(
        actor_item,
        Health(health),
        Psyche(psyche),
        Insanity(100),  # Insanity is always between 0 and 100.
        Strength(strength),
        Stamina(stamina),
        **kwargs,
    )
