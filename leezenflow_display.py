import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from displays import led_panel, terminal

class LeezenflowDisplay():
    display = None

    def setOutput(self,value):
        if (value == "led_panel"):
            self.display = led_panel.LED_Panel()
            self.display.GetDisplayType()
        elif (value == "terminal"):
            self.display = terminal.Terminal()
            self.display.GetDisplayType()
        else:
            self.display = led_panel.LED_Panel()
            self.display.GetDisplayType()