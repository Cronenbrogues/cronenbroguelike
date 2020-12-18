import logging

from adventurelib import Bag as _Bag

from engine.globals import G as _G
from engine import say


class Bag(_Bag):
    
    def _add_aliases(self, item):
        super()._add_aliases(item)
        logging.debug(f'_add_aliases called with {item}')
        item.holder = self
        if self is _G.player.inventory:
            say.insayne(f"You acquire {item.name}.")

    def _discard_aliases(self, item):
        super()._discard_aliases(item)
        item.holder = None
        if self is _G.player.inventory:
            say.insayne(f"You lose possession of {item.name}.")
