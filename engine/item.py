from adventurelib import Item as _Item


class Item(_Item):
    def __init__(self, name, *aliases, description=None):
        super().__init__(name, *aliases)
        if description is None:
            description = f"a {name}"
        self.description = description  # Fully mutable member.
