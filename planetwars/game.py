import sys
import logging
import signal
from planetwars.universe import Universe
from planetwars.util import timeout_handler, TimeIsUp
from time import time
from optparse import OptionParser

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
    It also instantiates your Bot implementaion in __init__.

    It supports a few command-line options call with "-h" to see a list.
    """
    def __init__(self, bot_class, timeout=0.95):
        options, _ = parser.parse_args()

        self.logging_enabled = bool(options.logfile)
        self.universe = Universe(self)
        self.bot = bot_class(self.universe)
        self.timeout = timeout
        self.turn_count = 0

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
                line = sys.stdin.readline().strip()
                if line.startswith("go"):
                    self.turn_count += 1
                    log.info("=== TURN START ===")
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
                        if self.logging_enabled:
                            log.error("Exception in bot.do_turn()", exc_info=True)
                        else:
                            raise
                    if self.has_alarm and has_itimer:
                        signal.setitimer(signal.ITIMER_REAL, 0)
                    log.info("### TURN END ### (time taken: %0.4f s)" % (time() - turn_start, ))
                    self.turn_done()
                else:
                    self.universe.update(line)
        except KeyboardInterrupt:
            # exit
            pass
        log.info("########### GAME END ########### (Turn count: %d)" % self.turn_count)
        

    def send_fleet(self, source_id, destination_id, ship_count):
        sys.stdout.write("%d %d %d\n" % (source_id, destination_id, ship_count))

    def turn_done(self):
        self.universe.turn_done()
        sys.stdout.write("go\n")
        sys.stdout.flush()

