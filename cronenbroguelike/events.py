from engine import event
from engine import say


class EphemeralTextEvent(event.Event):

    def __init__(self, text):
        super().__init__()
        self._text = text

    def execute(self):
        say.insayne(self._text)
        self._will_execute = False
