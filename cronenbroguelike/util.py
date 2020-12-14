from engine.globals import G as _G

from cronenbroguelike.events import EphemeralTextEvent as _EphemeralTextEvent


def enqueue_text(text, where="post"):
    """Convenience function to add text events to global queue."""
    _G.add_event(_EphemeralTextEvent(text), where)
