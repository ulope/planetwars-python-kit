from planetwars import BaseBot, Game
import random
from planetwars.universe import Universe

# This shows how you can add your own functionality to game objects (Universe in this case).

class StupidBot(BaseBot):
    """Modified StupidBot that uses new our own MyUniverse (see below)"""
    def do_turn(self):
        for p in self.universe.my_planets:
            if p.ship_count > 50:
                # my_and_nobodies_planets defined in MyUniverse below
                p.send_fleet(random.choice(list(self.universe.my_and_nobodies_planets)), p.ship_count / 2)

class MyUniverse(Universe):
    @property
    def my_and_nobodies_planets(self):
        return self.my_planets | self.nobodies_planets

Game(StupidBot, universe_class=MyUniverse)
