import sys
from logging import getLogger, basicConfig, DEBUG
import signal
import os

from planetwars.universe import Universe
from planetwars.util import timeout_handler, TimeIsUp
from time import time

log = getLogger(__name__)

class Game(object):
    def __init__(self, bot_class, timeout=0.95, logging_enabled=False):
        if logging_enabled:
            log_file = os.path.join(os.getcwd(), "planetwars.log")
            basicConfig(filename=log_file, level=DEBUG, format="%(asctime)s %(levelname)s: %(message)s")
            
        log.info("----------- GAME START -----------")
        self.universe = Universe(self)
        self.bot = bot_class(self.universe)
        self.timeout = timeout

        signal.signal(signal.SIGALRM, timeout_handler)
        try:
            #noinspection PyUnresolvedReferences
            import psyco
            psyco.full()
        except ImportError:
            pass
        self.main()

    def main(self):
        turn_count = 0
        has_itimer = True
        try:
            while True:
                line = sys.stdin.readline().strip()
                if line.startswith("go"):
                    log.info("=== TURN START ===")
                    turn_start = time()
                    try:
                        if has_itimer:
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
                        log.error("Exception in bot.do_turn()", exc_info=True)
                    if has_itimer:
                        signal.setitimer(signal.ITIMER_REAL, 0)
                    log.info("### TURN END ### (time taken: %0.4f s)" % (time() - turn_start, ))
                    turn_count += 1
                    self.turn_done()
                else:
                    self.universe.update(line)
        except KeyboardInterrupt:
            # exit
            pass
        log.info("########### GAME END ########### (Turn count: %d)" % turn_count)
        

    def send_fleet(self, source_id, destination_id, ship_count):
        sys.stdout.write("%d %d %d\n" % (source_id, destination_id, ship_count))

    def turn_done(self):
        self.universe.turn_done()
        sys.stdout.write("go\n")
        sys.stdout.flush()

