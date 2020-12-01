from adventurelib import Item as _Item


class _Statistic:
    def __init__(self, value):
        self._value = value

    def modify(self, delta):
        self._value += delta

    @property
    def value(self):
        surface_value = max(self._MIN_VALUE, self._value)
        surface_value = min(self._MAX_VALUE, surface_value)
        return surface_value

    @property
    def name(self):
        return self._NAME


class _BaseStatistic(_Statistic):
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
        'name', 'strength', 'stamina', 'will', 'wisdom', 'insanity'
    ]

    def __init__(self, actor_item, *statistics):
        self._actor_item = actor_item
        self._statistics = {
                statistic.name: statistic for statistic in statistics}

    # TODO: This sucks; using __getattr__ or something might help. Maybe just
    # hard-code the stats that all actors have? Dynamically add properties?
    # ... use metaclasses?
    def get_stat(self, stat_name):
        stat = self._statistics.get(stat_name)
        if stat is not None:
            return stat.value
        raise AttributeError

    def __getattr__(self, stat_name):
        try:
            return getattr(self._actor_item, stat_name)
        except AttributeError:
            return self.get_stat(stat_name)

    def mod_stat(self, stat_name, delta):
        stat = self._statistics.get(stat_name)
        if stat is not None:
            stat.modify(delta)
        else:
            raise AttributeError

    def all_stats(self):
        """Returns stat names and values in a reasonable order."""
        result = []

        # TODO: There's got to be a better way to do this.
        stat_order = self._CANONICAL_STAT_ORDER + sorted(
                self._statistics.keys() - set(self._CANONICAL_STAT_ORDER))
        return [
                (stat_name, getattr(self, stat_name))
                for stat_name in stat_order]


def create_actor(strength, stamina, will, wisdom, insanity, name, *aliases):
    """Convenience function to create actors with canonical stats."""
    actor_item = _Item(name, *aliases)
    return Actor(
        actor_item,
        Strength(strength),
        Stamina(stamina),
        Will(will),
        Wisdom(wisdom),
        Insanity(insanity),
    )
