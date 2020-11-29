class Event:
    
    def __init__(self):
        self.room = None
        self._ephemeral = True

    @property
    def ephemeral(self):
        return self._ephemeral

    def execute(self):
        return NotImplemented
