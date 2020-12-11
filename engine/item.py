from adventurelib import Item as _Item


# TODO: Maybe items should store a reciprocal reference to their containing
# inventory?
class Item(_Item):
    def __init__(self, *aliases, description=None):
        """Throws ValueError if no aliases are provided."""
        name, *aliases = aliases
        super().__init__(name, *aliases)
        if description is None:
            description = f"a {name}"
        self.description = description  # Fully mutable member.


class Consumable(Item):

    def consume(self, consumer):
        return NotImplemented


class Book(Item):

    def read(self, actor):
        return NotImplemented
