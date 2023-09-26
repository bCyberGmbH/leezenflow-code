import time
import argparse
from enum import Enum
from leezenflow.phase import TrafficLightPhase
from leezenflow.displays import led_panel, terminal
import leezenflow.shared_state as shared_state

parser = argparse.ArgumentParser()

parser.add_argument(
    "--display",
    help="Select the output device (Default: led_panel)",
    choices=["led_panel", "terminal"],
    default="led_panel",
    type=str,
)

parser.add_argument(
    "--phase",
    help="Which phase should be shown",
    choices=["green", "red", "yellow"],
    default="green",
    type=str,
)

parser.add_argument(
    "--height",
    help="How far should the Leezenflow Matrix be in percent",
    default=100,
    type=int,
)


class Bike_Status(Enum):
    RUNNING = 1
    RUNNING_FAST = 2
    STOPPING = 3
    STOPPED = 4


command_line_args = parser.parse_args()
display_arg = command_line_args.display

if display_arg == "led_panel":
    display = led_panel.LED_Panel()
else:
    display = terminal.Terminal()

phase_to_show_arg = command_line_args.phase
if phase_to_show_arg == "green":
    phase_to_show = TrafficLightPhase.GREEN
    is_moving = True
elif phase_to_show_arg == "red":
    phase_to_show = TrafficLightPhase.RED
    is_moving = False
elif phase_to_show_arg == "yellow":
    phase_to_show = TrafficLightPhase.YELLOW
    is_moving = True

height = command_line_args.height


def _animate_bike():
    display._draw_bike(
        255,
        255,
        255,
        8,
        8,
        moving=is_moving,
    )


def _draw_photo_mode():
    display.draw_leezenflow(height, phase_to_show)
    _animate_bike()
    display.update_frame()


while True:
    shared_state.global_traffic_light_data = phase_to_show
    _draw_photo_mode()
    time.sleep(1)
