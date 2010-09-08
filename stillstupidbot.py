from planetwars import BaseBot, Game, NOBODY, ENEMIES

class StillStupidBot(BaseBot):
    """Another stupid bot that spews out ships."""
    def do_turn(self):
        for p in self.universe.my_planets:
            if p.ship_count > 30:
                for target in self.universe.find_planets(growth_rate=set([5,4,3]), owner=NOBODY):
                    p.send_fleet(target, 10)
                    break

Game(StillStupidBot)
