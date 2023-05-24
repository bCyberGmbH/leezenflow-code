"""Simulate leezenflow behavior."""

import io
import re
import time

from leezenflow.message_interpreter import Interpreter
from message_modifier import ModifierHoerstertor
from shared_state import SharedState


class Simulation:
    # Tests that replays recorded phases
    def log_simulation(_, run_event):
        with io.open("sample_messages/august1.log", "r", encoding="utf8") as f:
            text = f.read()
        # spat_xml = re.split("(<SPATEM>)", text)
        spat_xml = re.findall("[\s\S]*?</SPATEM>", text)

        interpreter = Interpreter()
        modifier = ModifierHoerstertor()

        for spatem_xml in spat_xml:
            time.sleep(0.1)  # Test dataset has 10 updates per second -> 0.1
            shared = interpreter.interpret_message(spatem_xml)
            # shared = modifier.smooth(shared)
            SharedState.shared_data = shared
            print("Simulated: ", SharedState.shared_data, flush=True)
            if not run_event.is_set():
                break

    # Tests that replays recorded phases
    def mqtt_log(_, run_event):
        with io.open("sample_messages/spat.log", "r", encoding="utf8") as f:
            text = f.read()
        spat_xml = text.split("/rsu/forward/spat ")
        spat_xml = spat_xml[1:]  # Remove leading whitespace

        interpreter = Interpreter()

        for spatem_xml in spat_xml:
            time.sleep(0.1)  # Test dataset has 10 updates per second -> 0.1
            SharedState.shared_data = interpreter.interpret_message(spatem_xml)
            print("Simulated: ", SharedState.shared_data, flush=True)
            if not run_event.is_set():
                break

    # Tests a continous phase switch with fixed time
    def phase_switch_simulation(target, run_event):
        while run_event.is_set():
            for i in range(0, target):
                SharedState.shared_data = {
                    "current_phase": "green",
                    "current_timestamp": i,
                    "change_timestamp": target,
                    "hash": "A",
                }
                time.sleep(1)
                print(SharedState.shared_data)
                if not run_event.is_set():
                    break
            for i in range(0, target):
                SharedState.shared_data = {
                    "current_phase": "red",
                    "current_timestamp": i,
                    "change_timestamp": target,
                    "hash": "B",
                }
                time.sleep(1)
                print(SharedState.shared_data)
                if not run_event.is_set():
                    break

    # Tests a continous phase switch with all four phases red->red-yellow->green->yellow->...
    def phase_switch_simulation_4_phases(target, run_event):
        mini_phase = 1
        while run_event.is_set():
            for i in range(0, target):
                SharedState.shared_data = {
                    "current_phase": "red",
                    "current_timestamp": i,
                    "change_timestamp": target,
                    "hash": "R",
                }
                time.sleep(1)
                print(SharedState.shared_data)
                if not run_event.is_set():
                    break
            for i in range(0, mini_phase):
                SharedState.shared_data = {
                    "current_phase": "red-yellow",
                    "current_timestamp": i,
                    "change_timestamp": mini_phase,
                    "hash": "RY",
                }
                time.sleep(1)
                print(SharedState.shared_data)
                if not run_event.is_set():
                    break
            for i in range(0, target):
                SharedState.shared_data = {
                    "current_phase": "green",
                    "current_timestamp": i,
                    "change_timestamp": target,
                    "hash": "G",
                }
                time.sleep(1)
                print(SharedState.shared_data)
                if not run_event.is_set():
                    break
            for i in range(0, mini_phase):
                SharedState.shared_data = {
                    "current_phase": "yellow",
                    "current_timestamp": i,
                    "change_timestamp": mini_phase,
                    "hash": "Y",
                }
                time.sleep(1)
                print(SharedState.shared_data)
                if not run_event.is_set():
                    break

    # Tests a jumping non-steady prediction; e.g. from predicted 20 seconds, to 40 seconds, back to 10.
    def phase_update_simulation(color, run_event):
        timestamp = 0
        for i in range(0, 5):
            timestamp += 1
            SharedState.shared_data = {
                "current_phase": color,
                "current_timestamp": timestamp,
                "change_timestamp": 15,
                "hash": "A",
            }
            print(SharedState.shared_data)
            time.sleep(1)
            if not run_event.is_set():
                break
        for i in range(0, 10):
            timestamp += 1
            SharedState.shared_data = {
                "current_phase": color,
                "current_timestamp": timestamp,
                "change_timestamp": 50,
                "hash": "B",
            }
            time.sleep(1)
            print(SharedState.shared_data)
            if not run_event.is_set():
                break
        for i in range(0, 10):
            timestamp += 1
            SharedState.shared_data = {
                "current_phase": color,
                "current_timestamp": timestamp,
                "change_timestamp": 21,
                "hash": "C",
            }
            time.sleep(1)
            print(SharedState.shared_data)
            if not run_event.is_set():
                break

    # Tests high frequency updates
    def phase_fast_simulation(color, run_event):
        frequency = 10
        for i in range(0, 200):
            SharedState.shared_data = {
                "current_phase": color,
                "current_timestamp": int(i / frequency),
                "change_timestamp": 20,
                "hash": "A",
            }
            time.sleep(1 / frequency)
            print(SharedState.shared_data)
            if not run_event.is_set():
                break

    # Tests stale prediction
    def stale_prediction(_, run_event):
        while run_event.is_set():
            for i in range(3):
                SharedState.shared_data = {
                    "current_phase": "red",
                    "current_timestamp": i,
                    "change_timestamp": 3,
                    "hash": "A",
                }
                time.sleep(1)
                print(SharedState.shared_data)
                if not run_event.is_set():
                    break
            for i in range(10):
                SharedState.shared_data = {
                    "current_phase": "red",
                    "current_timestamp": 6.0 + i,
                    "change_timestamp": 6.0 + i,
                    "hash": "A",
                }
                time.sleep(1)
                print(SharedState.shared_data)
                if not run_event.is_set():
                    break
            for i in range(10):
                SharedState.shared_data = {
                    "current_phase": "green",
                    "current_timestamp": i,
                    "change_timestamp": 10,
                    "hash": "B",
                }
                time.sleep(1)
                print(SharedState.shared_data)
                if not run_event.is_set():
                    break
                if not run_event.is_set():
                    break
