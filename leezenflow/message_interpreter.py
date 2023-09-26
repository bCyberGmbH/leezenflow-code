"""Interpretation of the messages received from the traffic light."""

from datetime import timedelta
import logging
import time
import xml.etree.ElementTree as ET
import re
from xml.etree.ElementTree import ParseError

import leezenflow.shared_state as shared_state
from leezenflow.command_line_args import CommandLineArgs
from leezenflow.phase import TrafficLightPhase
from leezenflow.message_types import (
    MessageContentRaw,
    MessageContentParsed,
    MovementEventParsed,
    MovementEventRaw,
)


def convert_raw_message_to_parsed(message: MessageContentRaw) -> MessageContentParsed:
    movement_events_parsed = []

    for movement_event in message.movement_events:
        movement_event_parsed = MovementEventParsed(
            min_time=_calculate_remaining_phase_seconds(
                message.moy, message.time_stamp, movement_event.min_time
            ),
            max_time=_calculate_remaining_phase_seconds(
                message.moy, message.time_stamp, movement_event.max_time
            ),
            likely_time=_calculate_remaining_phase_seconds(
                message.moy, message.time_stamp, movement_event.likely_time
            ),
            current_phase=_convert_phase_to_enum(movement_event.current_phase),
            confidence=_convert_confidence_to_percentage(movement_event.confidence),
        )
        movement_events_parsed.append(movement_event_parsed)

    return MessageContentParsed(
        signal_group=message.signal_group,
        time_stamp=message.time_stamp,
        moy=message.moy,
        lsa_id=message.lsa_id,
        movement_events=movement_events_parsed,
    )


def _parse_xml(
    message: str,
    signal_group: int,
    lsa_id: int,
) -> MessageContentRaw:
    """Parse XML message and return selected content.

    Args:
        message: Raw XML message.
        signal_group: Signal group to be extacted.

    Raises:
        ParseError: Raised if root tag is not SPATEM.
        ValueError: Raised if signal_group in XML is not valid.
        AttributeError: Raised if tag in XML is not found with 'root.find'.

    Returns:
        MessageContentRaw: Dataclass with selected content.
    """

    # parse XML tree

    movement_events = []

    result = re.search(r"<stationID>(.*?)</stationID>", message)

    if result is None or int(result.group(1)) != lsa_id:
        raise ParseError("Intersection ID not found!")

    lsa_id = int(result.group(1))

    tree = ET.ElementTree(ET.fromstring(message))

    root = tree.getroot()

    if root.tag != "DATA":
        raise ParseError("root tag is not SPATEM")

    if not root.find("SPAT"):
        raise ParseError("root tag is not SPATEM")

    movement_state_node = root.find(
        f"SPAT/intersections/IntersectionState/states/MovementState[signalGroup='{signal_group}']"  # noqa: E501
    )
    if movement_state_node is None:
        raise ParseError(f"signalGroup {signal_group} not found!")

    time_stamp_node = root.find("SPAT/intersections/IntersectionState/timeStamp")
    if time_stamp_node is None or time_stamp_node.text is None:
        raise ParseError("timeStamp not found!")

    time_stamp = int(time_stamp_node.text)

    moy_node = root.find("SPAT/intersections/IntersectionState/moy")
    if moy_node is None or moy_node.text is None:
        raise ParseError("moy_node not found!")

    moy = int(moy_node.text)
    movement_event_nodes = movement_state_node.findall("state_time_speed/MovementEvent")
    if len(movement_event_nodes) == 0:
        raise ParseError("No MovementEvent nodes found")

    for movement_event_node in movement_event_nodes:
        min_time_node = movement_event_node.find("timing/minEndTime")
        if min_time_node is None or min_time_node.text is None:
            raise ParseError("minTime not found!")

        min_time = int(min_time_node.text)
        if min_time_node is None or min_time_node.text is None:
            raise ParseError("minTime not found!")

        max_time_node = movement_event_node.find("timing/maxEndTime")
        if max_time_node is None or max_time_node.text is None:
            raise ParseError("maxTime not found!")

        max_time = int(max_time_node.text)

        likely_time_node = movement_event_node.find("timing/likelyTime")
        if likely_time_node is None or likely_time_node.text is None:
            raise ParseError("likelyTime not found!")

        likely_time = int(likely_time_node.text)

        confidence = movement_event_node.find("timing/confidence")
        if confidence is None or confidence.text is None:
            raise ParseError("confidence not found!")

        confidence = int(confidence.text)

        phase = movement_event_node.find("eventState")
        if phase is None or phase.text is None:
            raise ParseError("phase not found!")
        phase = phase.text

        # create output dataclass
        movement_events.append(
            MovementEventRaw(
                min_time=min_time,
                max_time=max_time,
                likely_time=likely_time,
                current_phase=phase,
                confidence=confidence,
            )
        )

    message_content = MessageContentRaw(
        signal_group=signal_group,
        time_stamp=time_stamp,
        moy=moy,
        movement_events=movement_events,
        lsa_id=lsa_id,
    )
    return message_content


def _convert_phase_to_enum(phase: str) -> TrafficLightPhase:
    # translate phase to Enum

    if phase == "4":
        return TrafficLightPhase.RED_YELLOW
    elif phase == "7" or phase == "8":
        return TrafficLightPhase.YELLOW
    elif phase == "5" or phase == "6":
        return TrafficLightPhase.GREEN
    elif phase == "3":
        return TrafficLightPhase.RED
    else:
        raise ValueError(f"{phase=} is not valid!")


def _calculate_remaining_phase_seconds(
    moy: int, timestamp: int, time_mark: int
) -> timedelta:
    """time calculation to get remaining seconds.

    Args:
        moy: minute of year
        timestamp: current ms in hour
        time_mark: e.g. likelyTime of a phase in 1/10 s in hour

    Returns:
        current_timestamp: Current timestamp of the traffic light.
    """

    # cited from page 33 in https://www.car-2-car.org/fileadmin/documents/Basic_System_Profile/Release_1.5.0/C2CCC_RS_2077_InterpreterMAP_AutomotiveRequirements.pdf # noqa: E501
    # Data elements of type TimeMark (i.e. ‘startTime’, ‘minEndTime’, ‘maxEndTime’, ‘likelyTime’,  # noqa: E501
    # ‘nextTime’) shall represent 1/10 s in the hour in which the state change may occur (this may be the # noqa: E501
    # hour represented by the entry ‘moy’ or the following hour).
    # Note: If for the received TimeMark it holds that
    # TimeMark / 10 s < (moy modulo 60) min * 60 s/min,
    # the TimeMark corresponds to the hour following the hour represented by ‘moy’.

    # Clock: "hh : mm : ss" (e.g. 13:42:02)
    clock_minutes = moy % 60  # i.e. mm (e.g. 42)
    clock_seconds = timestamp / 1000  # i.e. ss (e.g. 02)

    if time_mark / 10 <= (moy % 60) * 60:  # If true, time_mark corresponds to next hour
        remaining_minutes_of_current_hour = 60 - clock_minutes
        remaining_seconds_of_current_hour = 60 - clock_seconds
        remaining_seconds_of_the_next_hour = time_mark / 10
        remaining_phase_seconds = (
            remaining_minutes_of_current_hour * 60
            + remaining_seconds_of_current_hour
            + remaining_seconds_of_the_next_hour
        )
    else:  # time_mark corresponds to current hour
        predicted_seconds_of_hour = time_mark / 10
        current_seconds_of_hour = clock_minutes * 60 + clock_seconds
        remaining_phase_seconds = predicted_seconds_of_hour - current_seconds_of_hour

    return timedelta(seconds=remaining_phase_seconds)


class Interpreter:
    @staticmethod
    def interpret_message(message):
        signal_group = CommandLineArgs.get_arguments().signal_group
        lsa_id = CommandLineArgs.get_arguments().lsa_id

        # extract message content from XML
        try:
            message_content = _parse_xml(message, signal_group, lsa_id)
        except ParseError:
            # HERE: Probably received malformated MAPEM or wrong lsa_id/signalGroup/likely_time > 36000. Just ignore message. # noqa: E501
            return
        except ValueError as e:
            logging.error("error in message_interpreter.py. exception: %s", e)
            return

        parsed = convert_raw_message_to_parsed(message_content)

        shared_state.last_message_timestamp = time.monotonic()
        shared_state.global_traffic_light_data = parsed


def _convert_confidence_to_percentage(confidence):
    if confidence == 0:
        return 21
    elif confidence == 1:
        return 36
    elif confidence == 2:
        return 47
    elif confidence == 3:
        return 56
    elif confidence == 4:
        return 62
    elif confidence == 5:
        return 68
    elif confidence == 6:
        return 73
    elif confidence == 7:
        return 77
    elif confidence == 8:
        return 81
    elif confidence == 9:
        return 85
    elif confidence == 10:
        return 88
    elif confidence == 11:
        return 91
    elif confidence == 12:
        return 94
    elif confidence == 13:
        return 96
    elif confidence == 14:
        return 98
    elif confidence == 15:
        return 100
    else:
        raise ValueError("unknown confidence value received")
