import paho.mqtt.client as mqtt

from shared_state import SharedState

class MQTTReceiver:
    def __init__(self, config, interpreter, flag_stats, statistics, logging, modify):
        self.mqtt_server_ip = config['mqtt']['server_ip']
        self.mqtt_server_port = int(config['mqtt']['server_port'])
        self.mqtt_topic =  config['mqtt']['topic']
        self.mqtt_client_name = config['mqtt']['client_name']
        self.mqtt_use_auth = config['mqtt']['use_auth']
        self.mqtt_client_user_name = config['mqtt']['client_user_name']
        self.mqtt_client_pw = config['mqtt']['client_pw']

        self.interpreter = interpreter
        self.flag_stats = flag_stats
        self.statistics = statistics
        self.logging = logging
        self.modify = modify

    def on_connect(self, client, userdata, flags, rc):
        print("mqtt topic: " + str(self.mqtt_topic))
        print("Connected with result code " + str(rc),flush=True)

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(self.mqtt_topic)

    def on_message(self, client, userdata, msg):
        shared_data = self.interpreter.interpret_message(str(msg.payload, "utf-8"))
        if self.flag_stats:
            self.statistics.save_message(shared_data)
        SharedState.shared_data =self.modify(shared_data)

        self.logging.info("Processed: " + str(SharedState.shared_data))    
        self.logging.debug(str(msg.payload, "utf-8"))
        print("Processed:",SharedState.shared_data,flush=True)

    def start(self)      
        client = mqtt.Client(client_id=self.mqtt_client_name)

        #client.tls_set()
        if self.mqtt_use_auth == "yes":
            client.username_pw_set(username=self.mqtt_client_user_name,password=self.mqtt_client_pw)

        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.connect(self.mqtt_server_ip, self.mqtt_server_port, 86400) # Timeout 1 day, default 60s

        return client