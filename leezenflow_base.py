import argparse
import time
import sys
import os
import threading

import paho.mqtt.client as mqtt
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import configparser
import logging
from logging.handlers import RotatingFileHandler

from message_interpreter import Interpreter
from simulations import Simulation

class LeezenflowBase(object):
    def __init__(self, command_line_args):
        try:    
            config = configparser.ConfigParser()
            config.read('config.ini')

            self.mqtt_server_ip = config['mqtt']['server_ip']
            self.mqtt_server_port = int(config['mqtt']['server_port'])
            self.mqtt_topic =  config['mqtt']['topic']
            self.mqtt_client_name = config['mqtt']['client_name']
            self.mqtt_use_auth = config['mqtt']['use_auth']
            self.mqtt_client_user_name = config['mqtt']['client_user_name']
            self.mqtt_client_pw = config['mqtt']['client_pw']
        except KeyError:
            print("Configuration file for MQTT missing...")

        self.args = command_line_args
            
        # Initialize status dictionary that is shared by the interpretation and animation logic
        self.shared_data = {
            "current_phase" : "awaiting_message",
            "current_timestamp" : 0,
            "change_timestamp" : 15,
            "hash" : 0 
        }

    def mqtt_client(self,_,run_event):

        def on_connect(client, userdata, flags, rc):
            print("mqtt topic: " + str(self.mqtt_topic))
            print("Connected with result code "+str(rc),flush=True)

            # Subscribing in on_connect() means that if we lose the connection and
            # reconnect then subscriptions will be renewed.
            client.subscribe(self.mqtt_topic)

        interpreter = Interpreter()

        if self.args.logging == 1:
            from message_modifier import ModifierHoerstertor
            modify = ModifierHoerstertor().smooth
        else:
            print("No modifier selected.")
            modify = lambda x: x # Return value unchanged

        def on_message(client, userdata, msg):
            #print(msg.topic+" "+str(msg.payload, "utf-8"),flush=True)
            shared_data = interpreter.interpret_message(str(msg.payload, "utf-8"))
            self.shared_data = modify(shared_data)

            logging.info("Processed: " + str(self.shared_data))    
            logging.debug(str(msg.payload, "utf-8"))
            print("Processed:",self.shared_data,flush=True)         
            
        client = mqtt.Client(client_id=self.mqtt_client_name)

        #client.tls_set()
        if self.mqtt_use_auth == "yes":
            client.username_pw_set(username=self.mqtt_client_user_name,password=self.mqtt_client_pw)

        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(self.mqtt_server_ip, self.mqtt_server_port, 86400) # Timeout 1 day, default 60s

        while run_event.is_set():
            client.loop()

    def run(self,_,run_event):
        print("Running")

    def process(self):

        log_name = 'log/console.log'
        if self.args.logging == 1:
            logging.basicConfig(filename=log_name, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.INFO)
            print("Writing log to file...",flush=True)
        elif self.args.logging == 2:
            logging.basicConfig(filename=log_name, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.DEBUG)
            print("Writing log to file...",flush=True)
        else:
            logging.basicConfig(filename=log_name, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.CRITICAL)

        log = logging.getLogger()
        handler = RotatingFileHandler(log_name, maxBytes=3e+8, backupCount=3) #300MB max
        log.addHandler(handler)

        options = RGBMatrixOptions()
        if self.args.led_gpio_mapping != None:
          options.hardware_mapping = self.args.led_gpio_mapping
        options.rows = self.args.led_rows
        options.cols = self.args.led_cols
        options.chain_length = self.args.led_chain
        options.parallel = self.args.led_parallel
        options.row_address_type = self.args.led_row_addr_type
        options.multiplexing = self.args.led_multiplexing
        options.pwm_bits = self.args.led_pwm_bits
        options.brightness = self.args.led_brightness
        options.pwm_lsb_nanoseconds = self.args.led_pwm_lsb_nanoseconds
        options.led_rgb_sequence = self.args.led_rgb_sequence
        options.pixel_mapper_config = self.args.led_pixel_mapper
        options.panel_type = self.args.led_panel_type
        if self.args.led_show_refresh:
          options.show_refresh_rate = 1
        if self.args.led_slowdown_gpio != None:
            options.gpio_slowdown = self.args.led_slowdown_gpio
        if self.args.led_no_hardware_pulse:
          options.disable_hardware_pulsing = True

        self.matrix = RGBMatrix(options = options)

        # Initialize threading
        run_event = threading.Event()
        run_event.set()

        t1 = threading.Thread(target = self.run, args = (None,run_event))

        if self.args.test == -1:
            t2 = threading.Thread(target = self.mqtt_client, args = (None,run_event))
        elif self.args.test == 0:
            self.shared_data = {
             "current_phase" : "red",
             "remaining_time" : 10
            }
            t2 = threading.Thread(target = lambda: print("No second thread."))
        elif self.args.test == 1:
            t2 = threading.Thread(target = Simulation.mqtt_client_simulation, args = (self,None,run_event))
        elif self.args.test == 2:
            t2 = threading.Thread(target = Simulation.mqtt_client_simulation_dataframe, args = (self,None,run_event))
        elif self.args.test == 3:
            t2 = threading.Thread(target = Simulation.phase_switch_simulation, args = (self,15,run_event))
        elif self.args.test == 4:
            t2 = threading.Thread(target = Simulation.phase_switch_simulation, args = (self,30,run_event))            
        elif self.args.test == 5:
            t2 = threading.Thread(target = Simulation.phase_update_simulation, args = (self,"red",run_event))
        elif self.args.test == 6:
            t2 = threading.Thread(target = Simulation.phase_fast_simulation, args = (self,"green",run_event))
        elif self.args.test == 7:
            t2 = threading.Thread(target = Simulation.stale_prediction, args = (self,None,run_event))
        else:
            raise Exception("Invalid test dataset argument.")

        # Start threads
        print("Press CTRL-C to stop leezenflow")
        t1.start()
        t2.start()

        try:
            while True:
                time.sleep(.1)
        except KeyboardInterrupt:
            print ("Attempting to close threads...")
            run_event.clear()
            t1.join()
            t2.join()
            print ("Threads successfully closed.")

        return True
