from planetwars.player import PLAYER_MAP
from planetwars.util import Point, TypedSetBase
from math import ceil, sqrt
import player

class Planet(object):
    def __init__(self, universe, id, x, y, owner, ship_count, growth_rate):
        self.universe = universe
        self.id = int(id)
        self.position = Point(float(x), float(y))
        self.owner = PLAYER_MAP.get(int(owner))
        self.ship_count = int(ship_count)
        self.growth_rate = int(growth_rate)

    def __repr__(self):
        return "<P(%d)@%s #%d +%d>" % (self.id, self.position, self.ship_count, self.growth_rate)

    def update(self, owner, ship_count):
        self.owner = PLAYER_MAP.get(int(owner))
        self.ship_count = int(ship_count)

    def distance(self, other):
        dx = self.position.x - other.position.x
        dy = self.position.y - other.position.y
        return int(ceil(sqrt(dx ** 2 + dy ** 2)))

    __sub__ = distance

    @property
    def attacking_fleets(self):
        """Hostile (as seen from this planets owner) fleets en-route to this planet."""
        return self.universe.find_fleets(destination=self, owner=player.EVERYBODY - self.owner)

    @property
    def reinforcement_fleets(self):
        """Friendly (as seen from this planets owner) fleets en-route to this planet."""
        return self.universe.find_fleets(destination=self, owner=self.owner)

    @property
    def sent_fleets(self):
        """Fleets owned by this planets owner sent from this planet."""
        return self.universe.find_fleets(source=self, owner=self.owner)

    def send_fleet(self, target, ship_count):
        """Sends a fleet to target. Also accepts a set of targets."""
        if isinstance(target, set):
            if self.ship_count >= ship_count * len(target):
                self.universe.send_fleet(self, target, ship_count)
            return
        if self.ship_count >= ship_count:
            self.universe.send_fleet(self, target, ship_count)

class Planets(TypedSetBase):
    accepts = (Planet, )
