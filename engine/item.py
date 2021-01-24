from adventurelib import Item as _Item


# TODO: Maybe items should store a reciprocal reference to their containing
# inventory?
# TODO: Inheritance was a bad move here. Composition would be better: each
# item can have a consumable, a readable, an ephemeral, etc. as members.
class Item(_Item):
    def __init__(
        self, *aliases, description=None, idle_description=None, obtainable=True
    ):
        """Throws ValueError if no aliases are provided."""
        name, *aliases = aliases
        super().__init__(name, *aliases)
        if description is None:
            description = f"a {name}"
        if idle_description is None:
            idle_description = f"There is a {name} lying on the ground."
        self.description = description  # Fully mutable member.
        self.idle_description = idle_description  # Fully mutable member.
        self.holder = None  # Fully mutable member.
        self._obtainable = obtainable

    @property
    def obtainable(self):
        return self._obtainable


class Consumable(Item):
    def consume(self, consumer):
        return NotImplemented


class Book(Item):
    def read(self, actor):
        return NotImplemented
