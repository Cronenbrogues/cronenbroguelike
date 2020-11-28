class Actor:

    def __init__(self):
        self._insanity = 0

    @property
    def insanity(self):
        return self._insanity

    @insanity.setter
    def insanity(self, new_value):
        new_value = max(0, new_value)
        new_value = min(100, new_value)
        self._insanity = new_value
