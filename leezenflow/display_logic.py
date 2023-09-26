"""Logic to calculate which phase in what state to display"""

import datetime
from datetime import timedelta
import logging
from typing import List, Optional, Tuple
from pydantic import BaseModel
from leezenflow.phase import TrafficLightPhase, DisplayPhase
import leezenflow.shared_state as shared_state


class DisplayMovementEvent(BaseModel):
    likely_time: timedelta
    current_phase: DisplayPhase


class DisplayLogic:
    def __init__(self, cli_args):
        self._display_phase = None
        self._shifted_seconds = 0
        self._shifted_seconds_yellow = 0
        self._phase_conversion = {
            TrafficLightPhase.GREEN: DisplayPhase.GREEN,
            TrafficLightPhase.YELLOW: DisplayPhase.GREEN,
            TrafficLightPhase.RED: DisplayPhase.RED,
            TrafficLightPhase.RED_YELLOW: DisplayPhase.RED,
        }
        self._previous_display_phase = {
            DisplayPhase.GREEN: DisplayPhase.RED,
            DisplayPhase.YELLOW: DisplayPhase.GREEN,
            DisplayPhase.RED: DisplayPhase.YELLOW,
            None: None,
        }
        self._init_speed_calculations(cli_args)

    def _init_speed_calculations(self, cli_args):
        bicycle_speed_arg = cli_args.bicycle_speed
        bicycle_yellow_speed_arg = cli_args.bicycle_yellow_speed
        distance_arg = cli_args.distance

        # calculate bike timings
        bicycle_speed_m_per_s = bicycle_speed_arg / 3.6  # calculate km/h to m/s
        bicycle_yellow_speed_m_per_s = (
            bicycle_yellow_speed_arg / 3.6
        )  # calculate km/h to m/s

        if distance_arg > 0 and bicycle_speed_arg > 0:
            self._shifted_seconds = (
                distance_arg / bicycle_speed_m_per_s
            )  # time = distance (in meter) / speed (in m/s)
            if bicycle_yellow_speed_arg > 0:
                self._shifted_seconds_yellow = self._shifted_seconds - (
                    distance_arg / bicycle_yellow_speed_m_per_s
                )

        logging.info(
            f"Time to reach traffic light normal: {self._shifted_seconds} and with fast speed: {self._shifted_seconds_yellow}"  # noqa: E501
        )

    def get_display_state(self) -> Optional[Tuple[float, DisplayPhase]]:
        state = shared_state.global_traffic_light_data
        if state is None:
            return
        display_movement_events: List[DisplayMovementEvent] = []

        phase = None
        time_left = None

        # transform event_state list into simpler Structure and inject yellow phase into movement_events # noqa: E501
        for movement_event in state.movement_events:
            display_movement_events.append(
                DisplayMovementEvent(
                    likely_time=movement_event.likely_time,
                    current_phase=self._phase_conversion[movement_event.current_phase],
                )
            )
            if (
                movement_event.current_phase == TrafficLightPhase.YELLOW
                and self._shifted_seconds_yellow > 0
            ):
                time_value = movement_event.likely_time + datetime.timedelta(
                    seconds=self._shifted_seconds_yellow
                )
                display_movement_events.append(
                    DisplayMovementEvent(
                        likely_time=time_value, current_phase=DisplayPhase.YELLOW
                    )
                )

        for movement_event in display_movement_events:
            likely_time = movement_event.likely_time.total_seconds()
            calculated_time_left = likely_time - self._shifted_seconds
            if calculated_time_left > 0:
                phase = movement_event.current_phase
                time_left = calculated_time_left
                break
            else:
                continue
        timings_debug_list = list(
            map(
                lambda e: (e.current_phase.name, e.likely_time.total_seconds()),
                state.movement_events,
            )
        )
        movement_events_debug_list = list(
            map(
                lambda e: (e.current_phase.name, e.likely_time.total_seconds()),
                display_movement_events,
            )
        )
        logging.debug(f"timings: {timings_debug_list}")
        logging.debug(f"movement events: {movement_events_debug_list}")
        logging.debug(f"time_left: {time_left} phase: {phase}")
        return_value = (time_left, phase)
        if phase is None:
            # shifted time is completely over given movement_events
            # fallback to opposite of last phase and use _shifted_seconds as value
            logging.debug("reached prediction horizon")
            last_phase = self._phase_conversion[state.movement_events[-1].current_phase]
            if last_phase == DisplayPhase.GREEN:
                return_value = (self._shifted_seconds, DisplayPhase.RED)
            if last_phase == DisplayPhase.RED:
                return_value = (self._shifted_seconds, DisplayPhase.GREEN)
        # check for "backwards" jump in phases and pin it to a high value until data catches up  # noqa: E501
        if self._shifted_seconds_yellow > 0:
            predicted_phase = return_value[1]
            previous_phase = self._previous_display_phase[self._display_phase]
            current_phase = self._display_phase
            logging.debug(
                f"predicted: {predicted_phase}, previous: {previous_phase}, current: {current_phase}"  # noqa: E501
            )
            if current_phase is not None and predicted_phase == previous_phase:
                logging.debug("prevented phase jump")
                return_value = (90, current_phase)
            else:
                self._display_phase = predicted_phase

        return return_value
