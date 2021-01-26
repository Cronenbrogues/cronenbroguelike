import collections
import copy
import random

from engine.globals import G as _G


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
    def __init__(self):
        self.owner = None  # Fully mutable member.

    def choose_action(self, unused_room, impulse=None):
        return NotImplemented


class HatesPlayer(AI):
    def choose_action(self, unused_room, impulse=None):
        # TODO: Is there an elegant way to make current_room aware of player?
        return _Action(Attack(target=_G.player, method=None))


class Chill(AI):
    def __init__(self):
        super().__init__()
        self._events = {}
        self._default_event = None

    def add_event(self, event, impulse):
        assert impulse is not None
        self._events.setdefault(impulse, set()).add(event)

    def add_default_event(self, event):
        # TODO: All of this owner stuff could be avoided by passing a context
        # to Event.execute() ...
        self._default_event = event

    def choose_action(self, unused_room, impulse=None):
        event_set = self._events.get(impulse, [self._default_event])
        result = random.sample(event_set, 1)[0]
        if result is not None:
            # TODO: deepcopy is a terrible way to fix this issue. Events should be
            # passes as classes, not instances. deepcopy absolutely barfs on
            # circular dependencies.
            result_copy = copy.deepcopy(result)
            result_copy.owner = self.owner
            event = Event(result_copy)
        else:
            event = None
        return _Action(event)
