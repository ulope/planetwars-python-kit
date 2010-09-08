class BaseBot(object):
    def __init__(self, universe):
        self.universe = universe

    def do_turn(self):
        raise NotImplementedError("You need to implement a 'do_turn' method in your Bot class.")

