import collections

import adventurelib

from engine import bag
from engine.globals import G as _G
from engine import say


# TODO: Just fork adventurelib; I need to hack it up so much to get it to work
# the way I want.
class Room(adventurelib.Room):

    DEFAULT_THEME = "neutral"
    THEME_TO_ROOMS = {}
    ALL_ROOMS = []

    def __init__(self, *args, **kwargs):
        theme = kwargs.pop("theme", self.DEFAULT_THEME)
        super().__init__(*args, **kwargs)

        self._display_exits = {}
        self._exits = {}

        # TODO: adventurelib.Bag should contain an ancillary set of aliases
        # to obviate O(n) lookup by alias.
        self._items = bag.Bag()
        self._characters = bag.Bag()
        self._corpses = bag.Bag()
        self._events = collections.deque()
        self.theme = theme

    def add_character(self, character):
        character.current_room = self
        self._characters.add(character)

    @property
    def corpses(self):
        return self._corpses

    @property
    def characters(self):
        return self._characters

    @property
    def npcs(self):
        return self._characters.difference({_G.player})

    def add_item(self, item):
        self._items.add(item)

    @property
    def items(self):
        return self._items

    @classmethod
    def create(cls, *args, **kwargs):
        result = cls(*args, **kwargs)
        cls.THEME_TO_ROOMS.setdefault(result.theme, []).append(result)
        cls.ALL_ROOMS.append(result)
        return result

    @classmethod
    def _add_exit(cls, source, destination, direction):
        exits = source._exits
        for description in direction.descriptions:
            assert description not in exits
            source._exits[description] = (destination, direction)
        source._display_exits[direction.display_description] = (destination, direction)

    def add_exit(self, direction, destination):
        self._add_exit(self, destination, direction)
        if direction.opposite is not None:
            self._add_exit(destination, self, direction.opposite)

    @property
    def display_exits(self):
        return self._display_exits.keys()

    @property
    def exits(self):
        return self._exits.keys()

    def _maybe_append_event(self, event):
        if event.will_execute:
            self._events.append(event)

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def add_event(self, event):
        # TODO: This is probably bad.
        event.room = self
        self._maybe_append_event(event)

    def events(self):
        # TODO: Rename this method.
        # TODO: Make Event.execute a generator.
        self._events.append(None)
        while True:
            next_event = self._events.popleft()
            if next_event is None:
                break
            yield next_event
            self._maybe_append_event(next_event)

    def __call__(self, *args, **kwargs):
        print(f"I was called with {args} and {kwargs}.")

    def exit(self, description):
        return self._exits.get(description, (None, None))

    def add_direction(self):
        return NotImplemented

    def north(self):
        return NotImplemented

    def south(self):
        return NotImplemented

    def east(self):
        return NotImplemented

    def west(self):
        return NotImplemented
