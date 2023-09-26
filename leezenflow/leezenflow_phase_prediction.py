import time
import logging
from leezenflow.phase import TrafficLightPhase
import leezenflow.shared_state as shared_state


class LeezenflowData:
    remaining_leezenflow_phase_time = 0.0
    current_leezenflow_phase = None


class LeezenflowPhasePrediction:
    def __init__(self, bicycle_speed_arg, bicycle_yellow_speed_arg, distance_arg):
        self.normal_speed = bicycle_speed_arg if bicycle_speed_arg > 0 else 0
        self.fast_speed = (
            bicycle_yellow_speed_arg if bicycle_yellow_speed_arg > 0 else 0
        )

        self.normal_speed_seconds = 0
        self.fast_speed_seconds = 0
        self.diff = 0

        # calculate bike timings
        bicycle_speed = self.normal_speed / 3.6  # calculate km/h to m/s
        bicycle_yellow_speed = self.fast_speed / 3.6  # calculate km/h to m/s
        distance = distance_arg if distance_arg > 0 else 0

        if distance > 0 and bicycle_speed > 0:
            self.normal_speed_seconds = (
                distance / bicycle_speed
            )  # time = distance (in meter) / speed (in m/s)
            if bicycle_yellow_speed > 0:
                self.fast_speed_seconds = (
                    distance / bicycle_yellow_speed
                )  # time = distance (in meter) / speed (in m/s)
                self.diff = (
                    self.normal_speed_seconds - self.fast_speed_seconds
                )  # difference in seconds between normal and fast bike to reach the traffic light # noqa: E501

        logging.info(
            f"Time to reach traffic light normal: {self.normal_speed_seconds} and with fast speed: {self.fast_speed_seconds}. Diff: {self.diff}"  # noqa: E501
        )

        self.current_phase_started = 0
        self.previous_phase = None

        self.first_run = True
        self.first_run_wait_info_printed = False

        self.early_switch_phase = False
        self.yellow_phase_started = False

        self.leezenflow_phase = None
        self.leezenflow_remaining_time = None

        self.leezenflow_data = LeezenflowData()

    def calculate_leezenflow_data(self, current_phase, remaining_time):
        if self.first_run is True:
            if self.first_run_wait_info_printed is False:
                self.first_run_wait_info_printed = True

            if (
                remaining_time
                + shared_state.global_traffic_light_data.get_phase_median_duration(
                    TrafficLightPhase.YELLOW
                )
                - self.normal_speed_seconds
                <= 0
            ):
                return None

            self.first_run = False

        if current_phase == TrafficLightPhase.RED and self.yellow_phase_started is True:
            self.yellow_phase_started = False

        if (
            remaining_time
            + shared_state.global_traffic_light_data.get_phase_median_duration(
                TrafficLightPhase.YELLOW
            )
            - self.normal_speed_seconds
            > 0
            and (
                current_phase is not TrafficLightPhase.YELLOW
                and current_phase is not TrafficLightPhase.RED_YELLOW
            )
            and self.yellow_phase_started is False
        ):
            self.early_phase = False
            self.leezenflow_phase = current_phase
            self.leezenflow_remaining_time = (
                remaining_time
                + shared_state.global_traffic_light_data.get_phase_median_duration(
                    TrafficLightPhase.YELLOW
                )
                - self.normal_speed_seconds
            )
        else:
            if self.early_phase is False:
                self.early_phase = True
                self.current_phase_started = time.monotonic()
                self.__calculate_early_switch_phase(remaining_time)
            self.__calculate_early_switch_time(remaining_time)
            if self.leezenflow_remaining_time <= 0:
                self.current_phase_started = time.monotonic()
                self.__calculate_early_switch_phase(remaining_time)

        self.leezenflow_data.remaining_leezenflow_phase_time = (
            self.leezenflow_remaining_time
        )
        self.leezenflow_data.current_leezenflow_phase = self.leezenflow_phase

        return self.leezenflow_data

    def __calculate_early_switch_phase(self, remaining_time):
        if self.leezenflow_phase == TrafficLightPhase.RED:
            self.leezenflow_phase = TrafficLightPhase.GREEN
            self.leezenflow_remaining_time = (
                shared_state.global_traffic_light_data.get_phase_median_duration(
                    TrafficLightPhase.GREEN
                )
                + shared_state.global_traffic_light_data.get_phase_median_duration(
                    TrafficLightPhase.YELLOW
                )
                - (time.monotonic() - self.current_phase_started)
            )
        elif self.leezenflow_phase == TrafficLightPhase.GREEN:
            self.yellow_phase_started = True
            self.leezenflow_phase = TrafficLightPhase.YELLOW

            if (
                remaining_time
                - shared_state.global_traffic_light_data.get_phase_median_duration(
                    TrafficLightPhase.YELLOW
                )
                < self.diff
            ):
                self.leezenflow_remaining_time = (
                    remaining_time
                    - shared_state.global_traffic_light_data.get_phase_median_duration(
                        TrafficLightPhase.YELLOW
                    )
                ) - (time.monotonic() - self.current_phase_started)
            else:
                self.leezenflow_remaining_time = self.diff - (
                    time.monotonic() - self.current_phase_started
                )

        elif self.leezenflow_phase == TrafficLightPhase.YELLOW:
            self.leezenflow_phase = TrafficLightPhase.RED
            self.leezenflow_remaining_time = (
                shared_state.global_traffic_light_data.get_phase_median_duration(
                    TrafficLightPhase.RED
                )
                + shared_state.global_traffic_light_data.get_phase_median_duration(
                    TrafficLightPhase.YELLOW
                )
                - self.diff
                - (time.monotonic() - self.current_phase_started)
            )

    def __calculate_early_switch_time(self, remaining_time):
        if (
            self.leezenflow_phase == TrafficLightPhase.RED
            or self.leezenflow_phase == TrafficLightPhase.GREEN
        ):
            if self.leezenflow_phase == TrafficLightPhase.RED:
                self.leezenflow_remaining_time = (
                    shared_state.global_traffic_light_data.get_phase_median_duration(
                        TrafficLightPhase.RED
                    )
                    + shared_state.global_traffic_light_data.get_phase_median_duration(
                        TrafficLightPhase.YELLOW
                    )
                    - self.diff
                    - (time.monotonic() - self.current_phase_started)
                )
            else:
                self.leezenflow_remaining_time = (
                    shared_state.global_traffic_light_data.get_phase_median_duration(
                        TrafficLightPhase.GREEN
                    )
                    + shared_state.global_traffic_light_data.get_phase_median_duration(
                        TrafficLightPhase.YELLOW
                    )
                    - (time.monotonic() - self.current_phase_started)
                )

        else:
            if (
                remaining_time
                - shared_state.global_traffic_light_data.get_phase_median_duration(
                    TrafficLightPhase.YELLOW
                )
                < self.diff
            ):
                self.leezenflow_remaining_time = (
                    remaining_time
                    - shared_state.global_traffic_light_data.get_phase_median_duration(
                        TrafficLightPhase.YELLOW
                    )
                ) - (time.monotonic() - self.current_phase_started)
            else:
                self.leezenflow_remaining_time = self.diff - (
                    time.monotonic() - self.current_phase_started
                )
