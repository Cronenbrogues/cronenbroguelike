import collections


class _GameState:

    def __init__(self):
        self.current_room = None

        self._text_queue = collections.deque()

    def enqueue_text(self, text):
        self._text_queue.append(text)

    def generate_text(self):
        while self._text_queue:
            yield self._text_queue.popleft()


G = _GameState()
