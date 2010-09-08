from planetwars import BaseBot, Game
import random

class StupidBot(BaseBot):
    """Stupid bot that randomly spews out ships."""
    def do_turn(self):
        for p in self.universe.my_planets:
            if p.ship_count > 50:
                p.send_fleet(random.choice(list(self.universe.not_my_planets)), p.ship_count / 2)

Game(StupidBot)
