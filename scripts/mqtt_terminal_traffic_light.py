import logging
import signal
import threading
import time

from leezenflow.command_line_args import CommandLineArgs
from leezenflow.receivers.mqtt import MQTTReceiverThread
import leezenflow.shared_state as shared_state
from leezenflow.simulation_display import _draw_traffic_light

stop_event = threading.Event()


def signal_handler(_signal, _frame):
    logging.info("Ctrl+C pressed. Stopping the thread...")
    stop_event.set()
    if receiver_thread is not None:
        receiver_thread.stop()


if __name__ == "__main__":
    cli_args = CommandLineArgs.get_arguments()
    if cli_args.log_file:
        logging.basicConfig(
            filename="log/leezenflow.log",
            level=cli_args.log_level,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
    else:
        logging.basicConfig(level=cli_args.log_level)

    signal.signal(signal.SIGINT, signal_handler)

    # ---
    # RECEIVER THREAD
    receiver_thread = MQTTReceiverThread(cli_args.lsa_id)

    receiver_thread.start()

    while not stop_event.is_set():
        data = shared_state.global_traffic_light_data

        if data is not None:
            phase = data.movement_events[0].current_phase
            remaining = data.movement_events[0].likely_time.total_seconds()
            moy = data.moy
            _draw_traffic_light(
                phase, remaining, moy, data.time_stamp, data.movement_events
            )
        time.sleep(0.1)
