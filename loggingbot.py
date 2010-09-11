from planetwars import BaseBot, Game
import random
from logging import getLogger

log = getLogger(__name__)

class LoggingBot(BaseBot):
    """Stupid bot that randomly spews out ships. This time with logging.
    While logging is enabled all exceptions your code throws will be catched
    and written into the logfile (including tracebacks).

    To enable logging start with "--log bla.log",  e.g:

    python loggingbot.py --log logfile.log

    Hint:
    Start with -h to see a list of all options.
    """
    def do_turn(self):
        log.info("I'm starting my turn")
        for p in self.universe.my_planets:
            if p.ship_count > 50:
                log.debug("Attacking from %s" % p)
                p.send_fleet(random.choice(list(self.universe.not_my_planets)), p.ship_count / 2)

Game(LoggingBot)
