import collections

import adventurelib

from engine import bag
from engine.globals import G as _G
from engine import say


class Room:

    DEFAULT_THEME = "neutral"
    REQUIRED = False
    THEME_TO_ROOMS = {}
    ALL_ROOMS = []

    def __init__(self):
        self._display_exits = {}
        self._exits = {}
        self._items = bag.Bag()
        self._characters = bag.Bag()
        self._corpses = bag.Bag()
        self._events = collections.deque()

    @property
    def display_exits(self):
        return self._display_exits.keys()

    @property
    def exits(self):
        return self._exits.keys()

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

    def on_enter(self, character=None):
        if character is None:
            character = _G.player
        self.add_character(character)

    def on_exit(self, character=None):
        if character is None:
            character = _G.player
        character.current_room = None
        self._characters.remove(character)

    def exit(self, description):
        return self._exits.get(description, (None, None))

    @property
    def items(self):
        return self._items

    def add_item(self, item):
        self._items.add(item)

    @property
    def corpses(self):
        return self._corpses

    @property
    def npcs(self):
        return self._characters.difference({_G.player})

    @property
    def characters(self):
        return self._characters

    def add_character(self, character):
        character.current_room = self
        self._characters.add(character)

    def _maybe_append_event(self, event):
        if event.will_execute:
            self._events.append(event)

    def add_event(self, event):
        # TODO: This is probably bad.
        self.event = event
        event.room = self

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

    @property
    def description(self):
        return self._DESCRIPTION

    @description.setter
    def description(self, new_description):
        """Getter will consult the class-level object until this is called.

        Thereafter, getter will consult the instance-level description.
        TODO: Use metaclasses to avoid this workaround.
        """
        self._DESCRIPTION = new_description

    def __init_subclass__(cls):
        for theme in cls._THEMES:
            cls.THEME_TO_ROOMS.setdefault(theme, []).append(cls)
        cls.ALL_ROOMS.append(cls)

    @classmethod
    def create_room_type(cls, name, description, themes=None):
        if not themes:
            themes = [cls.DEFAULT_THEME]

        result = type(
            name,
            (cls,),
            {
                "description": property(lambda _: description),
                "_THEMES": themes,
            },
        )
        return result

    @classmethod
    def create(cls):
        return cls()
