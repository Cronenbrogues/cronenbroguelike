import contextlib
import inspect
import logging

from adventurelib import when as _when

from engine.globals import G as _G


@contextlib.contextmanager
def _poll_context(poll_before, poll_after):
    logging.debug("Polling pre-events.")
    if poll_before:
        for event in _G.events("pre"):
            event.execute()
    yield
    logging.debug("Polling post-events.")
    if poll_after:
        for event in _G.events("post"):
            event.execute()


def when(command, context=None, **kwargs):
    poll_before = kwargs.pop('poll_before', False)
    poll_after = kwargs.pop('poll_after', False)

    def decorator(func):
        logging.debug("decorated function")

        def wrapped(*args, **new_kwargs):
            logging.debug("called wrapped")
            with _poll_context(poll_before, poll_after):
                logging.debug("returning from context")
                return func(*args, **new_kwargs)

        return _when(command, context=context, **kwargs)(wrapped)
            
    return decorator
