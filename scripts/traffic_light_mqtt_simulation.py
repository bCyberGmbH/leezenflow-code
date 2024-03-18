import time
import argparse

from leezenflow.message_interpreter import _parse_xml
from leezenflow.message_types import MessageContentRaw
from leezenflow.simulation_display import display_spat
import paho.mqtt.client as mqtt

parser = argparse.ArgumentParser()
parser.add_argument(
    "--lsa-id",
    action="store",
    help="Select the lsa id of the target intersection.",
    type=int,
    required=True,
)

parser.add_argument(
    "--log-file",
    action="store",
    help="Logfile with simulation data in it",
    type=str,
    required=True,
)

parser.add_argument(
    "--signal-group",
    action="store",
    help="Signal Group to display in Terminal (just for display purpose, complete XML with all signal groups is sent to mqtt)",  # noqa: E501
    type=int,
    required=True,
)

parser.add_argument(
    "--mqtt-host",
    action="store",
    help="mqtt host/broker to connect to",
    type=str,
    default="127.0.0.1",
)

command_line_args = parser.parse_args()


LOG_FILE = command_line_args.log_file
SIGNAL_GROUP = command_line_args.signal_group
LSA_ID = command_line_args.lsa_id

last_sent_time = 0
loop_work_start = 0
loop_work_end = 0

client = mqtt.Client()
client.connect(host=command_line_args.mqtt_host)


def handle_timing(parsed_message: MessageContentRaw):
    global last_sent_time, loop_work_start, loop_work_start
    if last_sent_time == 0:
        last_sent_time = parsed_message.moy * 60 + parsed_message.time_stamp / 1000
    else:
        message_time = parsed_message.moy * 60 + parsed_message.time_stamp / 1000
        passed_time = message_time - last_sent_time
        last_sent_time = message_time
        time.sleep(passed_time - min(loop_work_end - loop_work_start, 0))


with open(LOG_FILE) as f:
    current_message_string = ""
    for line in f:
        loop_work_start = time.monotonic()
        if len(current_message_string) != 0 and line.strip() == '<?xml version="1.0"?>':
            try:
                parsed_message = _parse_xml(
                    current_message_string, SIGNAL_GROUP, LSA_ID
                )
            except:  # noqa: E722
                print("discarded invalid message")
                current_message_string = line
                continue
            handle_timing(parsed_message)
            display_spat(parsed_message)
            client.publish(
                "/spat/" + str(command_line_args.lsa_id), current_message_string
            )
            current_message_string = line
        else:
            current_message_string += line
        loop_work_end = time.monotonic()


client.disconnect()
