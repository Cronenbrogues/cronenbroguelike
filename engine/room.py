import adventurelib
import collections


# TODO: Just fork adventurelib; I need to hack it up so much to get it work the
# way I want.
class Room(adventurelib.Room):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 

        # TODO: Directions need a "canonical" description; otherwise, listing
        # exits becomes confusing due to redundant descriptions.
        self._exits = {}

        # TODO: adventurelib.Bag should contain an ancillary set of aliases
        # to obviate O(n) lookup by alias.
        self._items = adventurelib.Bag()
        self._characters = adventurelib.Bag()
        self._events = collections.deque()

    @classmethod
    def _add_exit(cls, source, destination, descriptions):
        exits = source._exits
        for description in descriptions:
            assert(description not in exits)
            source._exits[description] = destination
    
    def add_exit(self, direction, destination):
        self._add_exit(self, destination, direction.descriptions)
        if direction.opposite is not None:
            self._add_exit(destination, self, direction.opposite.descriptions)

    def _maybe_append_event(self, event):
        if event.will_execute:
            self._events.append(event)

    def add_event(self, event):
        # TODO: This is probably bad.
        event.room = self
        self._maybe_append_event(event)

    @property
    def exits(self):
        return self._exits.keys()

    def events(self):
        self._events.append(None)
        while True:
            next_event = self._events.popleft()
            if next_event is None:
                break
            yield next_event
            self._maybe_append_event(next_event)

    def __call__(self, *args, **kwargs):
        print(f'I was called with {args} and {kwargs}.')

    def exit(self, description):
        return self._exits.get(description)
    
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
