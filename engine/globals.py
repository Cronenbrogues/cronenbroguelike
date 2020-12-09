import collections
import logging


class _GameState:

    def __init__(self):
        self.current_room = None
        self.player = None
        self._pre_events = collections.deque()
        self._post_events = collections.deque()
        self._text_queue = collections.deque()

    @classmethod
    def _maybe_append_event(cls, event, queue):
        if event.will_execute:
            logging.debug('Added event to global queue.')
            queue.append(event)

    def _queue_for(self, where):
        # TODO: Use an enum.
        assert where in {'pre', 'post'}
        return self._pre_events if where == 'pre' else self._post_events

    def add_event(self, event, where):
        queue = self._queue_for(where)
        self._maybe_append_event(event, queue)

    def events(self, where):
        queue = self._queue_for(where)
        # TODO: Rename this method.
        # TODO: Remove this method from Room.
        # TODO: Make Event.execute a generator to avoid this will_execute stuff.
        queue.append(None)
        while True:
            next_event = queue.popleft()
            if next_event is None:
                break
            yield next_event
            self._maybe_append_event(next_event, queue)

    def enqueue_text(self, text):
        self._text_queue.append(text)

    def generate_text(self):
        while self._text_queue:
            yield self._text_queue.popleft()


G = _GameState()
