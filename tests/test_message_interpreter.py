"""Test interpretation of messages."""

from datetime import timedelta
from dataclasses import dataclass
from pathlib import Path
from xml.etree.ElementTree import ParseError
from pydantic import ValidationError

from pytest import fixture, raises

from leezenflow.message_interpreter import (
    Interpreter,
    _parse_xml,
    MessageContentRaw,
    _calculate_remaining_phase_seconds,
)
from leezenflow.message_types import MovementEventRaw


@fixture(scope="function")
def interpreter():
    interpreter = Interpreter()
    return interpreter


@fixture(scope="function")
def sample_log() -> str:
    LOG_FILE = Path("tests/test_data/spat.xml")
    sample_log = LOG_FILE.read_text()
    return sample_log


@dataclass
class Arguments:
    """Class for mocking out command line arguments."""

    signal_group: int = 14
    lsa_id: int = 4070


def test_message_content_raw_class():
    raw_movemenet_event = MovementEventRaw(
        min_time=1, max_time=2, likely_time=3, current_phase="phase", confidence=1
    )
    content = MessageContentRaw(
        signal_group=1,
        time_stamp=30014,
        lsa_id=42,
        moy=215152,
        movement_events=[raw_movemenet_event],
    )
    assert content.signal_group, 1
    assert content.time_stamp, 30014
    assert content.moy, 215152
    assert content.movement_events, [raw_movemenet_event]


def test_message_content_raw_class_with_invalid_confidence():
    # test empty constructor
    with raises(ValidationError):
        MessageContentRaw()  # type: ignore

    # test invalid signal_group attribute
    with raises(ValidationError):
        MessageContentRaw(
            signal_group="",  # type: ignore
            time_stamp=30014,
            lsa_id=42,
            moy=215152,
            movement_events=[],
        )


def test__parse_xml(
    sample_log: str,
    interpreter: Interpreter,
    monkeypatch,
):
    message = sample_log

    # mock command line arguments "signal_group" to value 1 (present in sample log) # noqa: E501
    monkeypatch.setattr(
        "leezenflow.command_line_args.CommandLineArgs.get_arguments",
        lambda: Arguments(),
    )
    # run interpreter with sample log message and mocked command line arguments
    return_value = _parse_xml(message=message, signal_group=14, lsa_id=4070)

    # check if message is interpreted correctly
    assert return_value == MessageContentRaw(
        signal_group=14,
        lsa_id=4070,
        time_stamp=58718,
        moy=360534,
        movement_events=[
            MovementEventRaw(
                min_time=33120,
                max_time=33230,
                likely_time=33130,
                current_phase="3",
                confidence=13,
            ),
            MovementEventRaw(
                min_time=33140,
                max_time=33140,
                likely_time=33140,
                current_phase="4",
                confidence=15,
            ),
            MovementEventRaw(
                min_time=33520,
                max_time=33940,
                likely_time=33520,
                current_phase="5",
                confidence=3,
            ),
            MovementEventRaw(
                min_time=33540,
                max_time=33540,
                likely_time=33540,
                current_phase="7",
                confidence=15,
            ),
        ],
    )


def test_interpret_message_with_missing_signal_group():
    with raises(ParseError):
        message = "<SPATEM><spat><intersections><IntersectionState><timeStamp>12345</timeStamp><moy>123</moy><states><MovementState><state-time-speed><MovementEvent><timing><likelyTime>600</likelyTime></timing><eventState><pre-Movement></pre-Movement></eventState></MovementEvent></state-time-speed></MovementState></states></IntersectionState></intersections></spat></SPATEM>"  # noqa: E501
        _parse_xml(
            message, signal_group=42, lsa_id=42  # note: signalGroup is not in XML
        )


def test_interpret_message_with_invalid_xml(interpreter, monkeypatch):
    message = "<foo><bar>12345</bar></foo>"

    # mock command line arguments "signal_group" to value 1 (present in sample log) # noqa: E501
    monkeypatch.setattr(
        "leezenflow.command_line_args.CommandLineArgs.get_arguments",
        lambda: Arguments(),
    )

    result = interpreter.interpret_message(message)

    assert result is None


def test_interpret_message_with_malformed_xml():
    with raises(ParseError):
        message = "<foo><bar>12345</bar>"
        _parse_xml(message, signal_group=14, lsa_id=4070)


def test_interpret_message_with_non_xml():
    with raises(ParseError):
        message = "foo bar baz"
        _parse_xml(message, signal_group=14, lsa_id=4070)


def test_message_content_invalid_phase():
    with raises(ValueError):
        MessageContentRaw(
            signal_group=1,
            time_stamp=12345,
            moy=123,
            current_phase="foo",  # INVALID PHASE  # type: ignore
        )


def test__calculate_remaining_phase_seconds():
    # no idea if this is really right, but let's document the current state
    result = _calculate_remaining_phase_seconds(
        moy=208086, timestamp=6099, time_mark=3820
    )
    assert result == timedelta(seconds=15, microseconds=901000)


def test__calculate_remaining_phase_seconds_in_next_hour():
    # no idea if this is really right, but let's document the current state
    result = _calculate_remaining_phase_seconds(
        moy=208086, timestamp=6099, time_mark=3020
    )
    assert result == timedelta(seconds=3595, microseconds=901000)
