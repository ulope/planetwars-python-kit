from planetwars.players import PLAYER_MAP
from planetwars.util import Point
from math import ceil, sqrt

class Planet(object):
    def __init__(self, universe, id, x, y, owner, ship_count, growth_rate):
        self.universe = universe
        self.id = int(id)
        self.position = Point(float(x), float(y))
        self.owner = PLAYER_MAP.get(int(owner))
        self.ship_count = int(ship_count)
        self.growth_rate = int(growth_rate)

    def __repr__(self):
        return "<Planet %d at %s with %d ships>" % (self.id, self.position, self.ship_count)

    def update(self, owner, ship_count):
        self.owner = PLAYER_MAP.get(int(owner))
        self.ship_count = int(ship_count)

    def distance(self, other):
        dx = self.position.x - other.position.x
        dy = self.position.y - other.position.y
        return int(ceil(sqrt(dx ** 2 + dy ** 2)))

    __sub__ = distance

    @property
    def incoming_fleets(self):
        return self.universe.get_fleets_to(self)

    @property
    def outgoing_fleets(self):
        return self.universe.get_fleets_from(self)

    #def get_incoming_fleets_for(self, owner):


    def send_fleet(self, other, ship_count):
        if self.ship_count >= ship_count:
            self.universe.send_fleet(self, other, ship_count)
