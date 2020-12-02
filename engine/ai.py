from engine.globals import G


class AI:
    
    def choose_target(self, room):
        return NotImplemented


class HatesPlayer:
    
    def choose_target(self, unused_room):
        # TODO: Is there an elegant way to make current_room aware of player?
        return G.player
