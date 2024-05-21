import logging
import sys
import argparse
import time
from datetime import datetime
import threading
import paho.mqtt.client as mqtt
import re

parser = argparse.ArgumentParser()
parser.add_argument(
    "--lsa-id",
    action="store",
    help="Select the lsa id of the target intersection.",
    type=int,
    required=True,
)

command_line_args = parser.parse_args()


class MQTTReceiverCounterThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.mqtt_server_ip = "127.0.0.1"
        self.mqtt_server_port = 1883
        self.mqtt_topic = "/spat/#"
        self.mqtt_use_auth = "no"
        self.mqtt_client_user_name = ""
        self.mqtt_client_pw = ""
        self.client = mqtt.Client()
        self.message_count = 0
        self.start_time = 0.0
        self.lsa_id = command_line_args.lsa_id
        self.date_format = "%a %b %d %H:%M:%S %Y"
        self.current_minute = datetime.now().minute
        self.messages_in_current_minute = 0
        self.font_color = "\x1b[0m"

    def on_connect(self, client, userdata, flags, rc):
        logging.info("mqtt topic: " + str(self.mqtt_topic))
        logging.info("Connected with result code " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self.client.subscribe(self.mqtt_topic)

    def on_message(self, client, userdata, msg):
        result = re.search(r"<stationID>(.*?)</stationID>", str(msg.payload, "utf-8"))

        if result is None or int(result.group(1)) != self.lsa_id:
            return

        self.message_count += 1

    def run(self):
        if self.mqtt_use_auth == "yes":
            self.client.username_pw_set(
                username=self.mqtt_client_user_name, password=self.mqtt_client_pw
            )

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(
            self.mqtt_server_ip, self.mqtt_server_port, 65535
        )  # Timeout 65535s, default 60s

        self.client.loop_forever()

    def stop(self):
        self.client.disconnect()

    def output(self):
        if datetime.now().minute != self.current_minute:
            print(" -", self.messages_in_current_minute)
            print(
                datetime.now().strftime(receiver.date_format), "- ", end="", flush=True
            )
            self.current_minute = datetime.now().minute
            self.messages_in_current_minute = 0

        if receiver.message_count == 0:
            self.font_color = "\x1b[1;33;40m"
        else:
            self.font_color = "\x1b[0m"

        print(f"{self.font_color}{receiver.message_count}\x1b[0m|", end="", flush=True)
        self.messages_in_current_minute += receiver.message_count
        receiver.message_count = 0


receiver = MQTTReceiverCounterThread()
receiver.start()

print(
    f"{int(time.time())} {datetime.now().strftime(receiver.date_format)} SCRIPT START"
)

print(datetime.now().strftime(receiver.date_format), "- ", end="", flush=True)

try:

    elapsed_time = 0.0

    while True:
        receiver.start_time = time.time()
        receiver.output()
        elapsed_time = time.time() - receiver.start_time
        time.sleep(1 - elapsed_time)

except KeyboardInterrupt:
    receiver.stop()
