# Watchdog to monitor system and take actions on e.g. failure states

import logging
import threading
import time
import leezenflow.shared_state as shared_state


class WatchdogThread(threading.Thread):
    def __init__(self):
        logging.debug("WatchdogThread.__init__ called")
        threading.Thread.__init__(self)
        self.is_running = True

    def run(self):
        logging.info("Watchdog run()")

        while self.is_running:
            last_update = shared_state.last_message_timestamp
            if last_update != 0:
                now = time.monotonic()
                last_message_received_time = now - last_update
                if last_message_received_time >= 15:
                    if not shared_state.disable_display:
                        logging.warning("Watchdog disabled Display")
                        shared_state.disable_display = True
                else:
                    if shared_state.disable_display:
                        logging.info("Watchdog reenabled Display")
                        shared_state.disable_display = False
            time.sleep(0.1)

    def stop(self):
        self.is_running = False
