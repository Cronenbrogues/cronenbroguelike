import logging

from adventurelib import Bag as _Bag

from engine.globals import G as _G
from engine import say


class Bag(_Bag):

    # TODO: Fork adventurelib. This is getting to be too much.

    def _add_aliases(self, item, message=None):
        super()._add_aliases(item)
        logging.debug(f"_add_aliases called with {item}")
        item.holder = self
        if self is _G.player.inventory:
            message = message or f"You acquire {item.name}."
        if message is not None:
            say.insayne(message)

    def _discard_aliases(self, item, message=None):
        super()._discard_aliases(item)
        item.holder = None
        if self is _G.player.inventory:
            message = message or f"You lose possession of {item.name}."
        if message is not None:
            say.insayne(message)

    def add(self, item, message=None):
        set.add(self, item)
        self._add_aliases(item, message)

    def remove(self, item, message=None):
        set.remove(self, item)
        self._discard_aliases(item, message)
