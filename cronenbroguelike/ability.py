import sys as _sys

from engine import say as _say


_REGISTRY = {}


class _Ability:

    NAME = ""
    DESCRIPTION = ""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Disallows nameless abilities.
        # TODO: There must be a better mechanism for all this. Maybe just name
        # the abilities in minuscule?
        if cls.NAME:
            _REGISTRY[cls.NAME] = cls

    def __init__(self):
        self.owner = None

    def activate(self):
        return NotImplemented


class Meditation(_Ability):

    NAME = "meditation"
    DESCRIPTION = "Soothes the damaged mind; liberates the trapped soul."

    def activate(self):
        # TODO: Add global invocation counter.
        # TODO: Make events global and event polling constant so that this
        # ability can win the game.
        _say.insayne("You touch the ground. You sit and breathe, are still.")
        _say.insayne(
            "The stillness soothes your mind and steels your will.", add_newline=False
        )
        self.owner.insanity.heal_or_harm(-20)


# Makes all registered abilities importable by name.
for _key, _ability_class in _REGISTRY.items():
    setattr(_sys.modules[__name__], _key, _ability_class)


__all__ = list(_REGISTRY.keys())
