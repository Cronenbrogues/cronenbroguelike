class Ability:

    def __init__(self, name, description):
        self._description = description
        self._name = name
    
    def activate(self):
        pass

    @property
    def description(self):
        return self._description

    @property
    def name(self):
        return self._name


meditation = Ability(
        "meditation", "Soothes the damaged mind; liberates the trapped soul.")
