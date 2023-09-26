import logging
import os.path
import sys

from leezenflow.displays import led_panel, terminal

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
)


class LeezenflowDisplay:
    display = None

    def setOutput(self, value):
        if value == "terminal":
            self.display = terminal.Terminal()
        else:
            self.display = led_panel.LED_Panel()
        logging.info("display type value: %s", value)
