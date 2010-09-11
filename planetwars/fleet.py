from planetwars.player import PLAYER_MAP
from planetwars.util import TypedSetBase

class Fleet(object):
    def __init__(self, universe, id, owner, ship_count, source, destination, trip_length, turns_remaining):
        self.universe = universe
        self.id = int(id)
        self.owner = PLAYER_MAP.get(int(owner))
        self.ship_count = int(ship_count)
        self.source = self.universe._planets.get(int(source))
        self.destination = self.universe._planets.get(int(destination))
        self.trip_length = int(trip_length)
        self.turns_remaining = int(turns_remaining)

    def __repr__(self):
        return "<F(%d) #%d %s -> %s ETA %d>" % (self.id, self.ship_count, self.source, self.destination, self.turns_remaining)

class Fleets(TypedSetBase):
    accepts = (Fleet, )
