from planetwars.player import PLAYER_MAP
from planetwars.util import Point, TypedSetBase
from math import ceil, sqrt
import player

_dist_cache = {}

class Planet(object):
    def __init__(self, universe, id, x, y, owner, ship_count, growth_rate):
        self.universe = universe
        self.id = int(id)
        self.position = Point(float(x), float(y))
        self.owner = PLAYER_MAP.get(int(owner))
        self.ship_count = int(ship_count)
        self.growth_rate = int(growth_rate)

    def __repr__(self):
        return "<P(%d) #%d +%d>" % (self.id, self.ship_count, self.growth_rate)

    def update(self, owner, ship_count):
        self.owner = PLAYER_MAP.get(int(owner))
        self.ship_count = int(ship_count)

    def distance(self, other):
        """Returns the distance to <other>. <other> must be one of Planet instance, list, tuple or Point."""
        if not (self, other) in _dist_cache:
            if isinstance(other, Planet):
                ox = other.position.x
                oy = other.position.y
            elif isinstance(other, (list, tuple)):
                ox = other[0]
                oy = other[1]
            dx = self.position.x - ox
            dy = self.position.y - oy
            distance = int(ceil(sqrt(dx ** 2 + dy ** 2)))
            _dist_cache[(self, other)] = distance
            _dist_cache[(other, self)] = distance
        return _dist_cache[(self, other)]

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
        """Sends a fleet to target. Also accepts a set of targets.
        Returns the fleet(s) created by this action.
        """
        if isinstance(target, set):
            if self.ship_count >= ship_count * len(target):
                return self.universe.send_fleet(self, target, ship_count)
        else:
            if self.ship_count >= ship_count:
                return self.universe.send_fleet(self, target, ship_count)
        return None

class Planets(TypedSetBase):
    accepts = (Planet, )
