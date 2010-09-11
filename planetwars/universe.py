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
    """

    def __init__(self, game):
        self.game = game
        self.planets = {}
        self.fleets = {}
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
            return ret[0]
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
            return ret[0]
        return Planets()


    # Shortcut / Convenience properties
    @property
    def my_fleets(self):
        return self.find_fleets(owner=player.ME)

    @property
    def enemy_fleets(self):
        return self.find_fleets(owner=player.ENEMIES)

    @property
    def my_planets(self):
        return self.find_planets(owner=player.ME)

    @property
    def enemy_planets(self):
        return self.find_planets(owner=player.ENEMIES)

    @property
    def nobodies_planets(self):
        return self.find_planets(owner=player.NOBODY)

    @property
    def not_my_planets(self):
        return self.find_planets(owner=player.NOT_ME)

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
                new_planet = Planet(self, self.planet_id, *tokens[1:])
                self.planets[self.planet_id] = new_planet
                self.planet_id_map[id] = self.planet_id
                self._cache['p']['o'][new_planet.owner].add(new_planet)
                self._cache['p']['g'][new_planet.growth_rate].add(new_planet)
                self.planet_id += 1
        elif tokens[0] == "F":
            if len(tokens) != 7:
                raise ParsingException("Invalid format in gamestate: '%s'" % (game_state_line,))
            id = _make_id(*tokens[1:5])
            if id in self.fleets:
                self.fleets[id].update(tokens[6])
            else:
                new_fleet = Fleet(self, id, *tokens[1:])
                self.fleets[id] = new_fleet
                self._cache['f']['o'][new_fleet.owner].add(new_fleet)
                self._cache['f']['s'][new_fleet.source].add(new_fleet)
                self._cache['f']['d'][new_fleet.destination].add(new_fleet)

    def _update_planet(self, planet_id, values):
        planet = self.planets[self.planet_id_map[planet_id]]
        old_owner = planet.owner
        planet.update(*values)
        if planet.owner != old_owner:
            self._cache['p']['o'][old_owner].remove(planet)
            self._cache['p']['o'][planet.owner].add(planet)

    def send_fleet(self, source, destination, ship_count):
        log.debug("Sending fleet of %d from %s to %s." % (ship_count, source, destination))
        if isinstance(destination, set):
            for target in destination:
                self.game.send_fleet(source.id, target.id, ship_count)
            return
        self.game.send_fleet(source.id, destination.id, ship_count)

    def turn_done(self):
        for id, fleet in self.fleets.items():
            if fleet.turns_remaining == 1:
                self._cache['f']['o'][fleet.owner].remove(fleet)
                self._cache['f']['s'][fleet.source].remove(fleet)
                self._cache['f']['d'][fleet.destination].remove(fleet)
                del self.fleets[id]

