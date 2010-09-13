import sys
import logging
import signal
from planetwars.universe import Universe
from planetwars.util import timeout_handler, TimeIsUp
from time import time
from optparse import OptionParser
from planetwars.planet import Planet
from planetwars.fleet import Fleet

log = logging.getLogger(__name__)

parser = OptionParser()
parser.add_option("-l", "--log", dest="logfile", default=False,
                  help="Activate logging. Write log entries to FILE", metavar="FILE")
parser.add_option("--level", dest="loglevel", default="DEBUG", type="choice",
                  choices=["DEBUG", "INFO", "WARNING", "ERROR", "FATAL"],
                  help="Only log messages of LOGLEVEL or higher importance. "
                       "Valid levels are: DEBUG, INFO, WARNING, ERROR, FATAL. "
                       "Defaults to DEBUG.", metavar="LOGLEVEL")

class Game(object):
    """The Game object talks to the tournament engine and updates the universe.
    It supports a few command-line options call with "-h" to see a list.

    You should instantiate it with your BotClass as first argument, e.g:
    >>> Game(MyBot)

    Optionally you may supply your own universe, planet and fleet classes that are
    to be used instead of the default ones (e.g. your own Planet subclass that does something different).

    The timeout parameter specifies after which amout of time (in seconds) a TimeIsUp
    exception will be raised (by default this will abort the current turn and log a warning).
    This only works on platforms that support signal.SIGABRT (i.e. not windows) and on Python >= 2.6
    Unfortunately the tournament environment currently uses python 2.5 so you should not
    count on it beeing available.
    """
    def __init__(self, bot_class, universe_class=Universe, planet_class=Planet, fleet_class=Fleet, timeout=0.95):
        options, _ = parser.parse_args()

        self.logging_enabled = bool(options.logfile)
        self.universe = universe_class(self, planet_class=planet_class, fleet_class=fleet_class)
        self.bot = bot_class(self.universe)
        self.timeout = timeout
        self.turn_count = 0
        self._fleets_to_send = {}

        if self.logging_enabled:
            logging.basicConfig(filename=options.logfile, level=getattr(logging, options.loglevel), format="%(asctime)s %(levelname)s: %(message)s")
            
        log.info("----------- GAME START -----------")

        self.has_alarm = True
        try:
            signal.signal(signal.SIGALRM, timeout_handler)
        except AttributeError:
            # signal.SIGALRM not supported on this platform
            self.has_alarm = False
        try:
            #noinspection PyUnresolvedReferences
            import psyco
            psyco.full()
        except ImportError:
            pass
        self.main()

    def main(self):
        has_itimer = True
        try:
            while True:
                if sys.stdin.closed:
                    break
                line = sys.stdin.readline().strip()
                if line.startswith("go"):
                    self.turn_count += 1
                    log.info("=== TURN START === (Turn no: %d)" % self.turn_count)
                    turn_start = time()
                    try:
                        if self.has_alarm and has_itimer:
                            signal.setitimer(signal.ITIMER_REAL, self.timeout)
                    except AttributeError:
                        has_itimer = False
                        log.warning("signal.setitimer() is not available. Automatic timeout protection disabled!")
                    try:
                        self.bot.do_turn()
                    except TimeIsUp:
                        # Fallback in case bot doesn't catch it
                        log.warning("Bot failed to catch TimeIsUp exception!")
                        pass
                    except:
                        if not self.logging_enabled:
                            raise
                        log.error("Exception in bot.do_turn()", exc_info=True)
                    if self.has_alarm and has_itimer:
                        signal.setitimer(signal.ITIMER_REAL, 0)
                    log.info("### TURN END ### (time taken: %0.4f s)" % (time() - turn_start, ))
                    self.turn_done()
                else:
                    self.universe.update(line)
        except KeyboardInterrupt:
            # exit
            pass
        except:
            # This should not happen, but just in case
            if not self.logging_enabled:
                raise
            log.fatal("Error in game engine! Report at http://github.com/ulope/planetwars-python-kit/issues", exc_info=True)
        log.info("########### GAME END ########### (Turn count: %d)" % self.turn_count)
        

    def send_fleet(self, source_id, destination_id, ship_count):
        """Record fleets to send so we can aggregate them."""
        key = "%d.%d" % (source_id, destination_id)
        if key in self._fleets_to_send:
            self._fleets_to_send[key][2] += ship_count
        else:
            self._fleets_to_send[key] = [source_id, destination_id, ship_count]

    def turn_done(self):
        for source_id, destination_id, ship_count in self._fleets_to_send.values():
            sys.stdout.write("%d %d %d\n" % (source_id, destination_id, ship_count))
        self._fleets_to_send = {}
        sys.stdout.write("go\n")
        sys.stdout.flush()
        self.universe.turn_done()
