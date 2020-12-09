from cronenbroguelike.events import EphemeralTextEvent as _EphemeralTextEvent
from engine.globals import G as _G


def enqueue_text(text):
    """Convenience function to add text events to global queue."""
    _G.add_event(_EphemeralTextEvent(text), "post")
