from engine.globals import G
from engine import item

from cronenbroguelike import ability


class Book(item.Item):
    
    def read(self, actor):
        return NotImplemented


class MeditationBook(Book):
    
    def read(self, actor):
        if actor.has_read(self):
            # TODO: Condition pronoun/verb agreement on whether actor is
            # player or not. Make a utility function for this.
            if actor is G.player:
                say.insayne("You have already tasted the wisdom distilled in this book.")
            raise Exception

        else:
            actor.add_ability(ability.meditation)
            actor.set_has_read(self)
