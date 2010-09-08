from collections import defaultdict
from planetwars.util import ParsingException, _make_id
from planetwars.fleet import Fleet
from planetwars.planet import Planet
from planetwars import players

class Universe(object):
    def __init__(self, game):
        self.game = game
        self.planets = {}
        self.fleets = {}
        self.planet_id_map = {}
        self.planet_id = 0
        self._invalidate_cache()

    def _invalidate_cache(self):
        self._planets_by_owner = None
        self._fleets_by_owner = None
        self._fleets_by_destination = None
        self._fleets_by_source = None

    def _generate_fleet_owner_cache(self):
        if not self._fleets_by_owner:
            self._fleets_by_owner = defaultdict(list)
            for fleet in self.fleets.values():
                self._fleets_by_owner[fleet.owner].append(fleet)

    def _generate_planet_cache(self):
        if not self._planets_by_owner:
            self._planets_by_owner = defaultdict(list)
            for planet in self.planets.values():
                self._planets_by_owner[planet.owner].append(planet)

    @property
    def my_fleets(self):
        self._generate_fleet_owner_cache()
        return self._fleets_by_owner[players.ME]

    @property
    def their_fleets(self):
        self._generate_fleet_owner_cache()
        return self._fleets_by_owner[players.PLAYER2] + self._fleets_by_owner[players.PLAYER3] + self._fleets_by_owner[players.PLAYER4]

    def get_fleets_to(self, destination):
        if not self._fleets_by_destination:
            self._fleets_by_destination = defaultdict(list)
            for fleet in self.fleets.values():
                self._fleets_by_destination[fleet.destination.id].append(fleet)
        return self._fleets_by_destination[destination.id]

    def get_fleets_from(self, source):
        if not self._fleets_by_source:
            self._fleets_by_source = defaultdict(list)
            for fleet in self.fleets.values():
                self._fleets_by_source[fleet.source.id].append(fleet)
        return self._fleets_by_source[source.id]

    @property
    def my_planets(self):
        self._generate_planet_cache()
        return self._planets_by_owner[players.ME]

    @property
    def their_planets(self):
        self._generate_planet_cache()
        return self._planets_by_owner[players.PLAYER2] + self._planets_by_owner[players.PLAYER3] + self._planets_by_owner[players.PLAYER4]

    @property
    def nobodies_planets(self):
        self._generate_planet_cache()
        return self._planets_by_owner[players.NOBODY]


    def update(self, game_state_line):
        #log.debug("Game state: %s" % game_state_line)
        line = game_state_line.split("#")[0]
        tokens = line.split()
        if len(tokens) < 5:
            # Garbage - ignore
            return
        if tokens[0] == "P":
            if len(tokens) != 6:
                raise ParsingException("Invalid format in gamestate: '%s'" % (game_state_line,))
            id = _make_id(*tokens[1:3])
            if id in self.planet_id_map:
                #log.debug("updating planet %02d / %d" % (self.planet_id_map.get(id, -1), id))
                self.planets[self.planet_id_map[id]].update(*tokens[3:5])
            else:
                self.planets[self.planet_id] = Planet(self, self.planet_id, *tokens[1:])
                self.planet_id_map[id] = self.planet_id
                self.planet_id += 1
        elif tokens[0] == "F":
            if len(tokens) != 7:
                raise ParsingException("Invalid format in gamestate: '%s'" % (game_state_line,))
            id = _make_id(*tokens[1:5])
            if id in self.fleets:
                self.fleets[id].update(tokens[6])
            else:
                self.fleets[id] = Fleet(self, id, *tokens[1:])

    def send_fleet(self, source, destination, ship_count):
        self.game.send_fleet(source.id, destination.id, ship_count)

    def turn_done(self):
        self._invalidate_cache()
        for id, fleet in self.fleets.items():
            if fleet.turns_remaining == 1:
                del self.fleets[id]
