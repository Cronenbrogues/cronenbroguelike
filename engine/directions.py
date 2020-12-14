class Direction:
    def __init__(self, descriptions, opposite=None):
        self._display_description = descriptions[0]
        self._descriptions = descriptions
        self._opposite = opposite

    @property
    def display_description(self):
        return self._display_description

    @property
    def descriptions(self):
        return self._descriptions

    @property
    def opposite(self):
        return self._opposite

    # TODO: This is unnecessary nonsense.
    def _hash_criteria(self):
        return (
            (self._display_description,) + tuple(self._descriptions),
            self._opposite,
        )

    def __hash__(self):
        return hash((self._display_description,) + tuple(self._descriptions))

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return other == self
        return self._hash_criteria() == other._hash_criteria()

    @classmethod
    def make_oneway(cls, descriptions):
        return cls(descriptions)

    @classmethod
    def make_twoway(cls, descriptions, reverse_descriptions):
        out = cls.make_oneway(descriptions)
        back = cls(reverse_descriptions, opposite=out)
        out._opposite = back
        return out, back


# Make these into classes, not singletons--don't want two copies of the same
# direction.
north, south = Direction.make_twoway(["north"], ["south"])
east, west = Direction.make_twoway(["east"], ["west"])
purple, yellow = Direction.make_twoway(
    ["through a murky tunnel", "tunnel", "through the tunnel", "through tunnel"],
    ["by climbing a yawning sphincter", "sphincter", "through the sphincter"],
)
