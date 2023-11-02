import time
from enum import Enum
from leezenflow.phase import DisplayPhase
from leezenflow.displays import led_panel, terminal
from leezenflow.command_line_args import CommandLineArgs


class Bike_Status(Enum):
    RUNNING = 1
    RUNNING_FAST = 2
    STOPPING = 3
    STOPPED = 4


command_line_args = CommandLineArgs.get_arguments()
display_arg = command_line_args.display

if display_arg == "led_panel":
    display = led_panel.LED_Panel()
else:
    display = terminal.Terminal()

bike_height = 8
bike1_position = 8
bike2_position = -200
time_elapsed_bike = 0

last_bike_time = 0
start_time_bike = 0
bike_still_moving = False

update_interval = 0.01
matrix_height = 96
max_white = 255  # Maximum brightness of the white bike

bike_box_height = 23
bike_height = 8
bike_center = 8

color_green = (0, 255, 132)
color_red = (255, 49, 73)
color_yellow = (255, 255, 0)
placeholder_time_for_short_phases = 45

last_update_current_row = None
last_update_prediction_sec = None
last_update_elapsed_sec = 0
last_update_elapsed_time_start = 0
current_bike_status = None
last_phase = None
current_phase_time_start = 0.0
current_row = 0
remaining_real_time = 0

demo_distance = 195
demo_normal_speed = 18.3
demo_fast_speed = 25

demo_green_phase_time = 52
demo_yellow_phase_time = 8
demo_red_phase_time = 30

phase_start_time = 0
current_phase_time = 0
time_since_last_phase_start = 0

current_phase = DisplayPhase.RED
first_run = True


def _change_current_bike_status():
    global current_bike_status

    if current_phase == DisplayPhase.GREEN:
        current_bike_status = Bike_Status.RUNNING
    elif current_phase == DisplayPhase.YELLOW:
        current_bike_status = Bike_Status.RUNNING_FAST
    else:
        if (
            current_bike_status == Bike_Status.RUNNING
            or current_bike_status == Bike_Status.RUNNING_FAST
            or current_bike_status == Bike_Status.STOPPING
        ):
            current_bike_status = Bike_Status.STOPPING
        else:
            current_bike_status = Bike_Status.STOPPED


def get_next_bike_step(time_elapsed_bike, last_bike_time_local):
    global last_bike_time
    if time_elapsed_bike > last_bike_time_local + 0.05:
        last_bike_time = time_elapsed_bike
        return True


def _move_bikes_green(move_pixel_amount):
    global bike1_position, bike2_position, bike_still_moving

    bike_still_moving = False

    display._draw_bike(
        max_white,
        max_white,
        max_white,
        bike_height,
        bike1_position,
        moving=True,
    )
    if get_next_bike_step(time_elapsed_bike, last_bike_time):
        bike1_position += move_pixel_amount
        bike2_position += move_pixel_amount
    if bike1_position >= 37:
        bike1_position = -20
        bike2_position = 37
    if bike2_position >= 37:
        display._draw_bike(
            max_white,
            max_white,
            max_white,
            bike_height,
            bike2_position,
            moving=True,
        )
        if bike2_position >= 45:
            bike2_position = -999


def _move_bike_red():
    global bike1_position, bike2_position, bike_still_moving

    if bike_still_moving:
        display._draw_bike(
            max_white,
            max_white,
            max_white,
            bike_height,
            bike1_position,
            moving=True,
        )
        if get_next_bike_step(time_elapsed_bike, last_bike_time):
            bike1_position += 1
        if (
            bike1_position >= 45
        ):  # If the bike's position is beyond the center, the bike leaves the matrix and respawns in the center # noqa: E501
            bike1_position = -20
            bike_still_moving = False
        if (
            bike1_position == 8 + 1
        ):  # If the bike's position is before the center, the bike drives until the center is reached # noqa: E501
            bike_still_moving = False
    else:
        display._draw_bike(max_white, max_white, max_white, bike_height, bike_center)


def _animate_bike():
    if current_bike_status == Bike_Status.RUNNING:
        _move_bikes_green(1)
    elif current_bike_status == Bike_Status.RUNNING_FAST:
        _move_bikes_green(2)
    elif current_bike_status == Bike_Status.STOPPING:
        _move_bike_red()
    elif current_bike_status == Bike_Status.STOPPED:
        _move_bike_red()


def _switch_phase():
    global phase_start_time, time_since_last_phase_start, current_phase_time, current_phase, start_time_bike, time_elapsed_bike, last_bike_time  # noqa: E501
    phase_start_time = time.monotonic()
    time_since_last_phase_start = 0
    start_time_bike = time.monotonic()
    time_elapsed_bike = 0
    last_bike_time = 0

    if current_phase == DisplayPhase.GREEN:
        current_phase = DisplayPhase.YELLOW
        current_phase = DisplayPhase.YELLOW
        current_phase_time = demo_yellow_phase_time
    elif current_phase == DisplayPhase.YELLOW:
        current_phase = DisplayPhase.RED
        current_phase = DisplayPhase.RED
        current_phase_time = demo_red_phase_time
    elif current_phase == DisplayPhase.RED:
        current_phase = DisplayPhase.GREEN
        current_phase = DisplayPhase.GREEN
        current_phase_time = demo_green_phase_time

    _change_current_bike_status()


def _interpolate_value(total_time, current_time):
    global current_row

    start_value = bike_box_height
    end_value = matrix_height

    if current_time < 0 or current_time > total_time:
        return

    value_range = start_value - end_value
    value_per_second = value_range / total_time
    interpolated_value = start_value - (value_per_second * current_time)

    current_row = interpolated_value


while True:
    if first_run:
        first_run = False
        _switch_phase()

    time_since_last_phase_start = time.monotonic() - phase_start_time
    remaining_real_time = int(current_phase_time - time_since_last_phase_start)
    time_elapsed_bike = time.monotonic() - start_time_bike

    if time_since_last_phase_start >= current_phase_time:
        _switch_phase()

    _interpolate_value(current_phase_time, time_since_last_phase_start)

    prozent = round(
        100
        - ((current_row - bike_box_height) / (matrix_height - bike_box_height)) * 100
    )

    display.draw_leezenflow(prozent, current_phase)

    _animate_bike()

    display.update_frame()

    time.sleep(update_interval)
