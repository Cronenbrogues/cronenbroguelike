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
    def __init__(self, actor_item, *statistics):
        self._statistics = {statistic.name: statistic for statistic in statistics}

        # TODO: There's got to be a better way to do this.

    # TODO: This sucks; using __getattr__ or something might help. Maybe just
    # hard-code the stats that all actors have? Dynamically add properties?
    # ... use metaclasses?
    def getstat(self, stat_name):
        stat = self._statistics.get(stat_name)
        if stat is not None:
            return stat.value
        raise AttributeError

    def __getattr__(self, stat_name):
        return self.getstat(stat_name)

    def modstat(self, stat_name, delta):
        stat = self._statistics.get(stat_name)
        if stat is not None:
            stat.modify(delta)
        else:
            raise AttributeError


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
