import logging
import time
from enum import Enum
from typing import Optional

from leezenflow.command_line_args import CommandLineArgs
from leezenflow.displays import led_panel, terminal
import leezenflow.shared_state as shared_state
from leezenflow.phase import DisplayPhase
from leezenflow.display_logic import DisplayLogic


class Bike_Status(Enum):
    RUNNING = 1
    RUNNING_FAST = 2
    STOPPING = 3
    STOPPED = 4


class Animation:
    @staticmethod
    def run(stop_event):
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

        max_white = 255  # Maximum brightness of the white bike

        bike_box_height = 23
        bike_height = 8
        bike_center = 8

        current_bike_status = None
        current_row = 0

        minimum_anim_percent_value = 5
        last_percent_target = 100

        phase_start_time = 0
        time_since_last_phase_start = 0
        animation_current_phase: Optional[DisplayPhase] = None
        loop_start_time = 0
        is_blank = False

        display_logic = DisplayLogic(command_line_args)

        def _change_current_bike_status():
            nonlocal current_bike_status

            if animation_current_phase == DisplayPhase.GREEN:
                current_bike_status = Bike_Status.RUNNING
            elif animation_current_phase == DisplayPhase.YELLOW:
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
            nonlocal last_bike_time
            if time_elapsed_bike > last_bike_time_local + 0.05:
                last_bike_time = time_elapsed_bike
                return True

        def _move_bikes_green(move_pixel_amount):
            nonlocal bike1_position, bike2_position, bike_still_moving

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
            nonlocal bike1_position, bike2_position, bike_still_moving

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
                bike1_position = bike_center
                bike2_position = -999
                display._draw_bike(
                    max_white, max_white, max_white, bike_height, bike_center
                )

        def _animate_bike():
            if current_bike_status == Bike_Status.RUNNING:
                _move_bikes_green(1)
            elif current_bike_status == Bike_Status.RUNNING_FAST:
                _move_bikes_green(2)
            elif current_bike_status == Bike_Status.STOPPING:
                _move_bike_red()
            elif current_bike_status == Bike_Status.STOPPED:
                _move_bike_red()

        def _change_phase(new_phase: DisplayPhase):
            nonlocal phase_start_time, time_since_last_phase_start, animation_current_phase, start_time_bike, time_elapsed_bike, last_bike_time, last_percent_target, current_row  # noqa: E501
            phase_start_time = time.monotonic()
            time_since_last_phase_start = 0
            start_time_bike = time.monotonic()
            time_elapsed_bike = 0
            last_bike_time = 0
            last_percent_target = 100

            current_row = bike_box_height

            animation_current_phase = new_phase

            _change_current_bike_status()

        while not stop_event.is_set():
            display_state = display_logic.get_display_state()
            if shared_state.global_traffic_light_data is None or display_state is None:
                continue

            if shared_state.disable_display and not is_blank:
                logging.debug("blanking animation")
                display.fill(0, 0, 0)
                display.update_frame()
                is_blank = True
                continue

            if shared_state.disable_display and is_blank:
                continue

            if not shared_state.disable_display and is_blank:
                logging.debug("reenable animation")
                is_blank = False

            time_left, _ = display_state
            time_total = time_since_last_phase_start + time_left
            percent_target = time_left / time_total * 100

            loop_percent_step = 0
            # only progress if percantage is smaller, we do not jump "up"
            if percent_target < last_percent_target:
                loop_percent_step = (last_percent_target - percent_target) / 10

            for i in range(0, 10):
                loop_start_time = time.monotonic()
                display_state = display_logic.get_display_state()
                if display_state is None:
                    break
                _, phase = display_state
                if animation_current_phase != phase:
                    _change_phase(phase)
                    break

                time_since_last_phase_start = time.monotonic() - phase_start_time

                time_elapsed_bike = time.monotonic() - start_time_bike

                last_percent_target -= loop_percent_step

                percent = max(
                    minimum_anim_percent_value,
                    round(last_percent_target),
                )

                logging.debug(
                    f"animation: draw_leezenflow with phase {phase} and {percent}%)"
                )

                display.draw_leezenflow(percent, phase)

                _animate_bike()

                display.update_frame()

                time.sleep(max(0.1 - (time.monotonic() - loop_start_time), 0))
