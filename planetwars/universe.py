from planetwars.util import ParsingException, _make_id, SetDict
from planetwars.fleet import Fleet, Fleets
from planetwars.planet import Planet, Planets
from planetwars import player
from planetwars.player import Players
from logging import getLogger

log = getLogger(__name__)

class Universe(object):
    """'Main' planetwars object. The Universe knows about all planets and fleets and talks to the Game.

    It offers some convenience functions (e.g. my_planets, my_fleets, etc.) but the real power lies in
    the "find_fleets" and "find_planet" methods.

    Example:
    >>> universe.find_fleets(owner=player.ENEMIES, destination=universe.find_planets(owner=player.ME, growth_rate=5))
    This would return all hostile fleets en route to any of 'my' 5-growth planets.

    The game objects are stable. That means you can keep references to Planet and Fleet objects in you own code and
    they will still be valid in the next turn (although fleets of course will expire once they reach their destination).
    """

    def __init__(self, game, planet_class=Planet, fleet_class=Fleet):
        self.game = game
        self.planet_class = planet_class
        self.fleet_class = fleet_class
        self._planets = {}
        self._fleets = {}
        self.planet_id_map = {}
        self.planet_id = 0
        self._cache = {
            "f": {
                "o": SetDict(Fleets),
                "s": SetDict(Fleets),
                "d": SetDict(Fleets),
            },
            "p": {
                "o": SetDict(Planets),
                "g": SetDict(Planets),
            }
        }

    def find_fleets(self, owner=None, source=None, destination=None):
        """
        Returns a set of fleets that matches *all* (i.e. boolean and) criteria.
        All parameters accept single or set arguments (e.g. player.ME vs. player.ENEMIES).

        Returns <Fleets> (@see fleet.py) objects (a set subclass).
        """
        ret = []
        if owner:
            ret.append(self._cache["f"]["o"][Players(owner)])
        if source:
            ret.append(self._cache["f"]["s"][Planets(source)])
        if destination:
            ret.append(self._cache["f"]["d"][Planets(destination)])
        if ret:
            if len(ret) > 1:
                return reduce(lambda x, y: x & y, ret[1:], ret[0])
            return Fleets(ret[0])
        return Fleets()

    def find_planets(self, owner=None, growth_rate=None):
        """
        Returns a set of planets that matches *all* (i.e. boolean and) criteria.
        All parameters accept single or set arguments (e.g. player.ME vs. player.ENEMIES).

        Returns <Planets> (@see planet.py) objects (a set subclass).
        """
        ret = []
        if owner:
            ret.append(self._cache["p"]["o"][Players(owner)])
        if growth_rate:
            ret.append(self._cache["p"]["g"][growth_rate])

        if ret:
            if len(ret) > 1:
                return ret[0] & ret[1]
            return Planets(ret[0])
        return Planets()


    # Shortcut / Convenience properties
    @property
    def fleets(self):
        """Returns all fleets."""
        return self.find_fleets(owner=player.EVERYBODY)

    # Alias for fleets
    all_fleets = fleets

    @property
    def my_fleets(self):
        """Returns all fleets send by ME"""
        return self.find_fleets(owner=player.ME)

    @property
    def enemy_fleets(self):
        """Returnes all fleets send by another player"""
        return self.find_fleets(owner=player.ENEMIES)

    @property
    def planets(self):
        """All planets."""
        return self.find_planets(owner=player.EVERYBODY)

    # Alias for planets
    all_planets = planets

    @property
    def my_planets(self):
        """Returns all planets belonging to ME."""
        return self.find_planets(owner=player.ME)

    @property
    def enemy_planets(self):
        """Returns all planets belonging to another player."""
        return self.find_planets(owner=player.ENEMIES)

    @property
    def nobodies_planets(self):
        """Returns all planets belonging to NOBODY."""
        return self.find_planets(owner=player.NOBODY)

    @property
    def not_my_planets(self):
        """Returns all planets *not* belonging to ME."""
        return self.find_planets(owner=player.NOT_ME)


    def send_fleet(self, source, destination, ship_count):
        log.debug("Sending fleet of %d from %s to %s." % (ship_count, source, destination))
        if isinstance(destination, set):
            new_fleets = Fleets()
            for target in destination:
                source.ship_count -= ship_count
                self.game.send_fleet(source.id, target.id, ship_count)
                trip_length = source.distance(target)
                new_fleets.add(self._add_fleet(player.ME.id, ship_count, source.id, target.id, trip_length, trip_length))
            return new_fleets
        else:
            source.ship_count -= ship_count
            self.game.send_fleet(source.id, destination.id, ship_count)
            trip_length = source.distance(destination)
            return self._add_fleet(player.ME.id, ship_count, source.id, destination.id, trip_length, trip_length)

    # Internal methods below. You should never need to call any of these yourself.
    #############

    def update(self, game_state_line):
        """Update the game state. Gets called from Game."""
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
                self._update_planet(id, tokens[3:5])
            else:
                new_planet = self.planet_class(self, self.planet_id, *tokens[1:])
                self._planets[self.planet_id] = new_planet
                self.planet_id_map[id] = self.planet_id
                self._cache['p']['o'][new_planet.owner].add(new_planet)
                self._cache['p']['g'][new_planet.growth_rate].add(new_planet)
                self.planet_id += 1
        elif tokens[0] == "F":
            if len(tokens) != 7:
                raise ParsingException("Invalid format in gamestate: '%s'" % (game_state_line,))
            self._add_fleet(*tokens[1:])

    def _update_planet(self, planet_id, values):
        planet = self._planets[self.planet_id_map[planet_id]]
        old_owner = planet.owner
        planet.update(*values)
        if planet.owner != old_owner:
            self._cache['p']['o'][old_owner].remove(planet)
            self._cache['p']['o'][planet.owner].add(planet)

    def _add_fleet(self, *args):
        id = _make_id(*args)
        if id in self._fleets:
            # (fleets already updated by turn_done)
            return self._fleets[id]
        else:
            new_fleet = self.fleet_class(self, id, *args)
            self._fleets[id] = new_fleet
            self._cache['f']['o'][new_fleet.owner].add(new_fleet)
            self._cache['f']['s'][new_fleet.source].add(new_fleet)
            self._cache['f']['d'][new_fleet.destination].add(new_fleet)
            return new_fleet

    def turn_done(self):
        _fleets = {}
        for id, fleet in self._fleets.items():
            fleet.turns_remaining -= 1
            # Ugh.. Since fleets have no id in the engine we have to make sure they match next turn
            new_id = _make_id(fleet.owner.id, fleet.ship_count, fleet.source.id, fleet.destination.id, fleet.trip_length, fleet.turns_remaining)
            if fleet.turns_remaining == 0:
                self._cache['f']['o'][fleet.owner].remove(fleet)
                self._cache['f']['s'][fleet.source].remove(fleet)
                self._cache['f']['d'][fleet.destination].remove(fleet)
            else:
                _fleets[new_id] = fleet
        self._fleets = _fleets

