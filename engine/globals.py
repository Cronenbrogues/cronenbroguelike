import collections
import contextlib
import inspect
import logging


class _GameState:
    def __init__(self):
        self._pre_events = collections.deque()
        self._post_events = collections.deque()
        self._text_queue = collections.deque()
        self.reset()

    def reset(self):
        self.current_room = None
        self.player = None
        self.cause_of_death = None
        self.just_died = False
        self._pre_events.clear()
        self._post_events.clear()
        self._text_queue.clear()

    @classmethod
    def _maybe_append_event(cls, event, queue):
        if event.will_execute:
            logging.debug(f"Added event {event} to global queue.")
            queue.append(event)
        else:
            logging.debug(f"Removing event {event}.")

    def _queue_for(self, where):
        # TODO: Use an enum.
        assert where in {"pre", "post"}
        return self._pre_events if where == "pre" else self._post_events

    def add_event(self, event, where):
        queue = self._queue_for(where)
        self._maybe_append_event(event, queue)

    def events(self, where):
        logging.debug(f'Events called with where={where}')
        queue = self._queue_for(where)
        new_queue = []
        new_queue.extend(queue)
        queue.clear()
        logging.debug(f'Queue is {queue}')
        logging.debug(f'new_queue is {new_queue}')
        # TODO: Rename this method.
        # TODO: Remove this method from Room.
        # TODO: Make Event.execute a generator to avoid this will_execute stuff.
        for next_event in new_queue:
            logging.debug(f'next_event is {next_event}')
            if next_event.will_execute:
                yield next_event
            self._maybe_append_event(next_event, queue)

    def enqueue_text(self, text):
        self._text_queue.append(text)

    def generate_text(self):
        while self._text_queue:
            yield self._text_queue.popleft()

    def set_flag(self, flag):
        logging.debug('set_flag called')

    def clear_queues(self):
        logging.debug('Killing all events.')
        for queue in [self._pre_events, self._post_events]:
            for event in queue:
                if event is not None:
                    event.kill()
            queue.clear()


G = _GameState()


@contextlib.contextmanager
def poll_events(poll_before=True, poll_after=True):
    logging.debug("Polling pre-events.")
    if poll_before:
        for event in G.events("pre"):
            if event.will_execute:
                event.execute()
    yield
    logging.debug("Polling post-events.")
    if poll_after:
        for event in G.events("post"):
            if event.will_execute:
                event.execute()
