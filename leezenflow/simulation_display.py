from datetime import datetime, timedelta

"""Display an ASCII traffic + other info from a SPATEM Message
This is intended for simulated traffic light data"""

from leezenflow.message_interpreter import (
    MessageContentRaw,
    convert_raw_message_to_parsed,
)
from leezenflow.phase import TrafficLightPhase


def _draw_traffic_light(phase, remaining_seconds, moy, timestamp):
    line_up = "\033[1A"
    line_clear = "\x1b[2K"

    # clear previous output
    for x in range(6):
        print(line_up, end=line_clear)
    if phase == TrafficLightPhase.RED_YELLOW:  # red + yellow (when a red phase ends)
        print("\033[1;31m\u2B24\033[0;0m")
        print("\033[1;33m\u2B24\033[0;0m")
        print("\033[1;32m()\033[0;0m")
    elif phase == TrafficLightPhase.YELLOW:
        print("\033[1;31m()\033[0;0m")
        print("\033[1;33m\u2B24\033[0;0m")
        print("\033[1;32m()\033[0;0m")
    elif phase == TrafficLightPhase.GREEN:
        print("\033[1;31m()\033[0;0m")
        print("\033[1;33m()\033[0;0m")
        print("\033[1;32m\u2B24\033[0;0m")
    elif phase == TrafficLightPhase.RED:
        print("\033[1;31m\u2B24\033[0;0m")
        print("\033[1;33m()\033[0;0m")
        print("\033[1;32m()\033[0;0m")
    else:
        raise ValueError(f"simulation_display: Got Unknown Phase - {phase}")

    print("------")
    print(f"remaining phase seconds: { remaining_seconds}s")
    print(f"SPAT timestamp: {_calculate_timestamp(moy, timestamp)}")


def _calculate_timestamp(moy, timestamp):
    clock_seconds = timestamp / 1000

    start_of_year = datetime(datetime.now().year, 1, 1)

    current_timestamp = start_of_year + timedelta(minutes=moy, seconds=clock_seconds)
    current_timestamp_with_timezone = current_timestamp + timedelta(hours=2)

    return current_timestamp_with_timezone.strftime("%H:%M:%S")


def display_spat(unparsed_message: MessageContentRaw):
    message = convert_raw_message_to_parsed(unparsed_message)

    _draw_traffic_light(
        message.movement_events[0].current_phase,
        message.movement_events[0].likely_time.total_seconds(),
        message.moy,
        message.time_stamp,
    )
