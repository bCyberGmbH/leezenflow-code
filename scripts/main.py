import logging
import signal
import threading

from leezenflow.animation import Animation
from leezenflow.watchdog import WatchdogThread
from leezenflow.command_line_args import CommandLineArgs

from leezenflow.receivers.simulation import SimulationThread
from leezenflow.receivers.mqtt import MQTTReceiverThread

receiver_thread = None
prediction_thread = None
animation_thread = None
watchdog_thread = None
stop_event = threading.Event()


def signal_handler(_signal, _frame):
    logging.info("Ctrl+C pressed. Stopping the thread...")
    stop_event.set()
    if watchdog_thread is not None:
        watchdog_thread.stop()
    if receiver_thread is not None:
        receiver_thread.stop()
    if prediction_thread is not None:
        prediction_thread.join()
    if animation_thread is not None:
        animation_thread.join()


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
    if cli_args.receiver == "mqtt":
        receiver_thread = MQTTReceiverThread()
    elif cli_args.receiver == "simulation":
        receiver_thread = SimulationThread()
    else:
        raise ValueError("Receiver Command Line Argument is wrong!")
    receiver_thread.start()

    # ---
    # ANIMATION THREAD

    animation_thread = threading.Thread(target=Animation.run, args=(stop_event,))
    animation_thread.start()

    # ---
    # WATCHDOG THREAD

    watchdog_thread = WatchdogThread()
    watchdog_thread.start()
