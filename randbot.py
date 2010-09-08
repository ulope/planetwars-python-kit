from planetwars import BaseBot, Game
import random

class RandBot(BaseBot):
    def do_turn(self):
        for p in self.universe.my_planets:
            if p.ship_count > 50:
                p.send_fleet(random.choice(self.universe.nobodies_planets + self.universe.their_planets), p.ship_count / 2)

Game(RandBot)
