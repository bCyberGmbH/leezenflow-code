import logging
from leezenflow.displays import display


class DummyDisplay(display.AbstractLeezenflowDisplay):
    def __init__(self):
        logging.warning("DummyDisplay active.")

    def update_frame(self):
        pass

    def set_pixel(self, row, pixel, r, g, b):
        pass

    def generate_table(self):
        pass
