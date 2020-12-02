from adventurelib import Item as _Item


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
        self._value += delta

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

    @property
    def current_value(self):
        return self._current_value

    def heal_or_harm(self, delta):
        surface_value = self._value
        if self._MIN_VALUE is not None:
            surface_value = max(self._MIN_VALUE, surface_value)
        if self._MAX_VALUE is not None:
            surface_value = min(self._MAX_VALUE, surface_value)
        self._current_value += delta
        self._current_value = min(self._current_value, self._value)


class Health(_VariableStatistic):
    _NAME = "health"

    def heal_or_harm(self, delta):
        super().heal_or_harm(delta)
        if self._current_value <= 0:
            self._owner.die()


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


class Actor:

    _CANONICAL_STAT_ORDER = [
        'health', 'psyche', 'strength', 'stamina', 'will', 'wisdom', 'insanity'
    ]

    def __init__(self, actor_item, *statistics, **kwargs):
        self._actor_item = actor_item
        self._statistics = {}
        for statistic in statistics:
            self._statistics[statistic.name] = statistic
            statistic.owner = self
        self._ai = kwargs.pop('ai', None)

    @property
    def ai(self):
        return self._ai

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
                self._statistics.keys() - set(self._CANONICAL_STAT_ORDER))
        return [self._statistics[stat_name] for stat_name in stat_order]

    def die(self):
        from engine import say
        say.insayne(f'{self.name.title()} has died!')


def create_actor(
        health, psyche, strength, stamina, will, wisdom, insanity, name,
        *aliases, **kwargs):
    """Convenience function to create actors with canonical stats."""
    actor_item = _Item(name, *aliases)
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
