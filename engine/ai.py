import collections

from engine.globals import G


# Action types.
class Attack(collections.namedtuple('Attack', ['target', 'method'])):
    pass


class _Action:

    def __init__(self, action_type):
        self._action_type = action_type

    @property
    def attack(self):
        if isinstance(self._action_type, Attack):
            return self._action_type


class AI:

    def choose_action(self, room):
        return NotImplemented


class HatesPlayer(AI):

    def choose_action(self, unused_room):
        # TODO: Is there an elegant way to make current_room aware of player?
        return _Action(Attack(target=G.player, method=None))
