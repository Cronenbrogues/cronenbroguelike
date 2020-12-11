import collections

from engine import event
from engine.globals import G


# Action types.
class Attack(collections.namedtuple("Attack", ["target", "method"])):
    pass


class Speak(collections.namedtuple("Attack", ["target", "message"])):
    pass


class Event(collections.namedtuple("Event", ["event"])):
    pass


class _Action:
    def __init__(self, action_type):
        self._action_type = action_type

    @property
    def attack(self):
        if isinstance(self._action_type, Attack):
            return self._action_type

    @property
    def speak(self):
        if isinstance(self._action_type, Speak):
            return self._action_type

    @property
    def event(self):
        if isinstance(self._action_type, Event):
            return self._action_type


class AI:
    def choose_action(self, room):
        return NotImplemented


class HatesPlayer(AI):
    def choose_action(self, unused_room):
        # TODO: Is there an elegant way to make current_room aware of player?
        return _Action(Attack(target=G.player, method=None))


class Librarian(AI):
    def __init__(self):
        self._event = None

    def add_event(self, event):
        self._event = event

    def choose_action(self, unused_room):
        return _Action(Event(self._event))
