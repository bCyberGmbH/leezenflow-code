"""Test the message_interpreter module."""

import io
import re

from leezenflow.message_interpreter import Interpreter


def test_interpret_message():
    """Test interpreting messages."""

    # load test data
    with io.open("sample_messages/august1.log", "r", encoding="utf8") as f:
        text = f.read()
    xml_segments = re.findall("[\s\S]*?</SPATEM>", text)
    xml_segment = xml_segments[0]

    # parse message
    interpreter = Interpreter()
    message = interpreter.interpret_message(xml_segment)
    seconds_until_change = message["change_timestamp"] - message["current_timestamp"]

    # check result
    assert message["current_phase"] == "green"
    assert seconds_until_change == 3.0
