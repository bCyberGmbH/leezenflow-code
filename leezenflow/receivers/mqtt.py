import logging
import threading
import paho.mqtt.client as mqtt

from leezenflow.message_interpreter import Interpreter


class MQTTReceiverThread(threading.Thread):
    def __init__(self, lsa_id, on_message_function=None):
        threading.Thread.__init__(self)
        self.mqtt_server_ip = "127.0.0.1"
        self.mqtt_server_port = 1883
        self.mqtt_topic = "/spat/" + str(lsa_id)
        self.mqtt_use_auth = "no"
        self.mqtt_client_user_name = ""
        self.mqtt_client_pw = ""
        self.on_message_function_override = on_message_function
        self.client = mqtt.Client()

    def on_connect(self, client, userdata, flags, rc):
        logging.info("mqtt topic: " + str(self.mqtt_topic))
        logging.info("Connected with result code " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self.client.subscribe(self.mqtt_topic)

    def on_message(self, client, userdata, msg):
        Interpreter.interpret_message(str(msg.payload, "utf-8"))

    def run(self):
        if self.mqtt_use_auth == "yes":
            self.client.username_pw_set(
                username=self.mqtt_client_user_name, password=self.mqtt_client_pw
            )

        self.client.on_connect = self.on_connect

        if self.on_message_function_override is not None:
            self.client.on_message = self.on_message_function_override
        else:
            self.client.on_message = self.on_message

        self.client.connect(
            self.mqtt_server_ip, self.mqtt_server_port, 65535
        )  # Timeout 65535s, default 60s

        self.client.loop_forever()

    def stop(self):
        self.client.disconnect()
