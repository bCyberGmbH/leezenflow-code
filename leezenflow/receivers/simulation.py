from datetime import timedelta
import io
import logging
import threading
import time

from leezenflow.command_line_args import CommandLineArgs
import leezenflow.shared_state as shared_state
from leezenflow.phase import TrafficLightPhase

from leezenflow.message_interpreter import Interpreter


class SimulationThread(threading.Thread):
    def __init__(self):
        logging.debug("SimulationThread.__init__ called")
        super().__init__()
        self.running = False

    def run(self):
        logging.debug("SimulationThread.run called")
        self.running = True
        cli_args = CommandLineArgs.get_arguments()
        simulation_method = getattr(SimulationThread, cli_args.simulation)
        logging.info("Starting Simulation %s", cli_args.simulation)
        simulation_method(self)

    def stop(self):
        logging.debug("SimulationThread.stop called")
        self.running = False

    def log_simulation(self):
        with io.open(
            "sample_messages/lf-ms-z-2023-08-30-12-35.log.txt", "r", encoding="utf8"
        ) as f:
            text = f.read()
        spat_xml = text.split('<?xml version="1.0"?>')

        for spatem_xml in spat_xml:
            time.sleep(1)  # Test dataset has 10 updates per second -> 0.1
            Interpreter.interpret_message(spatem_xml)
            if not self.running:
                break

    # Tests a continous phase switch with fixed time
    def phase_switch_simulation(self):
        green_phases = [10, 9, 8, 7, 6, 9, 4, 7, 4, 9, 3, 6, 2, 1, 0]

        small_phase_time_seconds = 2
        print("phase_switch_simulation started")
        while self.running:
            for i in green_phases:
                shared_state.global_traffic_light_data.update(
                    TrafficLightPhase.GREEN, timedelta(seconds=i)
                )
                time.sleep(1)
                if not self.running:
                    break
            for i in range(0, small_phase_time_seconds):
                shared_state.global_traffic_light_data.update(
                    TrafficLightPhase.YELLOW,
                    timedelta(seconds=small_phase_time_seconds - i),
                )
                time.sleep(1)
                if not self.running:
                    break
            for i in green_phases:
                shared_state.global_traffic_light_data.update(
                    TrafficLightPhase.RED, timedelta(seconds=i)
                )
                time.sleep(1)
                if not self.running:
                    break
            for i in range(0, small_phase_time_seconds):
                shared_state.global_traffic_light_data.update(
                    TrafficLightPhase.RED_YELLOW,
                    timedelta(seconds=small_phase_time_seconds - i),
                )
                time.sleep(1)
                if not self.running:
                    break

    # Tests a continous phase switch with fixed time
    def phase_switch_simulation_original(self):
        phase_time_seconds = 10
        small_phase_time_seconds = 2
        print("phase_switch_simulation started")
        while self.running:
            for i in range(0, phase_time_seconds):
                shared_state.global_traffic_light_data.update(
                    TrafficLightPhase.GREEN, timedelta(seconds=(phase_time_seconds - i))
                )
                time.sleep(1)
                if not self.running:
                    break
            for i in range(0, small_phase_time_seconds):
                shared_state.global_traffic_light_data.update(
                    TrafficLightPhase.YELLOW,
                    timedelta(seconds=(small_phase_time_seconds - i)),
                )
                time.sleep(1)
                if not self.running:
                    break
            for i in range(0, phase_time_seconds):
                shared_state.global_traffic_light_data.update(
                    TrafficLightPhase.RED, timedelta(seconds=(phase_time_seconds - i))
                )
                time.sleep(1)
                if not self.running:
                    break
            for i in range(0, small_phase_time_seconds):
                shared_state.global_traffic_light_data.update(
                    TrafficLightPhase.RED_YELLOW,
                    timedelta(seconds=(small_phase_time_seconds - i)),
                )
                time.sleep(1)
                if not self.running:
                    break
