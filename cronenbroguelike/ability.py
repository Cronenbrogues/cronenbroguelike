class Ability:

    def __init__(self, description):
        self._description = description
    
    def activate(self):
        pass

    @property
    def description(self):
        return self._description


meditation = Ability("Soothes the damaged mind; liberates the trapped soul.")
