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

from mqtt_message_interpreter import Interpreter
from smoother import HoersterTorSmoother
from simulations import Simulation

class LeezenflowBase(object):
    def __init__(self, *args, **kwargs):
        
        config = configparser.ConfigParser()
        config.read('config.ini')

        self.mqtt_server_ip = config['mqtt']['server_ip']
        self.mqtt_server_port = int(config['mqtt']['server_port'])
        self.mqtt_topic =  config['mqtt']['topic']
        self.mqtt_client_name = config['mqtt']['client_name']
        self.mqtt_use_auth = config['mqtt']['use_auth']
        self.mqtt_client_user_name = config['mqtt']['client_user_name']
        self.mqtt_client_pw = config['mqtt']['client_pw']
            
        # Use Dict such that data can be written at the same  time
        self.shared_data = {
            "current_phase" : "awaiting_message",
            "remaining_time" : 30
        }

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-r", "--led-rows", action="store", help="Display rows. 16 for 16x32, 32 for 32x32. Default: 32", default=32, type=int)
        self.parser.add_argument("--led-cols", action="store", help="Panel columns. Typically 32 or 64. (Default: 32)", default=96, type=int)
        self.parser.add_argument("-c", "--led-chain", action="store", help="Daisy-chained boards. Default: 1.", default=1, type=int)
        self.parser.add_argument("-P", "--led-parallel", action="store", help="For Plus-models or RPi2: parallel chains. 1..3. Default: 1", default=1, type=int)
        self.parser.add_argument("-p", "--led-pwm-bits", action="store", help="Bits used for PWM. Something between 1..11. Default: 11", default=11, type=int)
        self.parser.add_argument("-b", "--led-brightness", action="store", help="Sets brightness level. Default: 100. Range: 1..100", default=100, type=int)
        self.parser.add_argument("-m", "--led-gpio-mapping", help="Hardware Mapping: regular, adafruit-hat, adafruit-hat-pwm" , choices=['regular', 'adafruit-hat', 'adafruit-hat-pwm'], default='adafruit-hat-pwm',type=str)
        self.parser.add_argument("--led-scan-mode", action="store", help="Progressive or interlaced scan. 0 Progressive, 1 Interlaced (default)", default=1, choices=range(2), type=int)
        self.parser.add_argument("--led-pwm-lsb-nanoseconds", action="store", help="Base time-unit for the on-time in the lowest significant bit in nanoseconds. Default: 130", default=130, type=int)
        self.parser.add_argument("--led-show-refresh", action="store_true", help="Shows the current refresh rate of the LED panel")
        self.parser.add_argument("--led-slowdown-gpio", action="store", help="Slow down writing to GPIO. Range: 0..4. Default: 1", default=3, type=int) #3 best while testing at Swarco; 2 for local mqtt test
        self.parser.add_argument("--led-no-hardware-pulse", action="store", help="Don't use hardware pin-pulse generation")
        self.parser.add_argument("--led-rgb-sequence", action="store", help="Switch if your matrix has led colors swapped. Default: RGB", default="RGB", type=str)
        self.parser.add_argument("--led-pixel-mapper", action="store", help="Apply pixel mappers. e.g \"Rotate:90\"", default="Rotate:0", type=str)
        self.parser.add_argument("--led-row-addr-type", action="store", help="0 = default; 1=AB-addressed panels; 2=row direct; 3=ABC-addressed panels; 4 = ABC Shift + DE direct", default=0, type=int, choices=[0,1,2,3,4])
        self.parser.add_argument("--led-multiplexing", action="store", help="Multiplexing type: 0=direct; 1=strip; 2=checker; 3=spiral; 4=ZStripe; 5=ZnMirrorZStripe; 6=coreman; 7=Kaler2Scan; 8=ZStripeUneven... (Default: 0)", default=0, type=int)
        self.parser.add_argument("--led-panel-type", action="store", help="Needed to initialize special panels. Supported: 'FM6126A'", default="", type=str)

        self.parser.add_argument("--test", action="store", help="Use test dataset. Default: -1; no test", default=-1, type=int)
        self.parser.add_argument("--logging", action="store", help="1=Log all messages. Default:0 ", default=0, type=int)

    def mqtt_client(self,_,run_event):
        self.shared_data = {
            "current_phase" : "awaiting_message"
        }
        print(self.shared_data)

        interpreter = Interpreter()
        smoother = HoersterTorSmoother()

        def on_connect(client, userdata, flags, rc):
            print("mqtt topic: " + str(self.mqtt_topic))
            print("Connected with result code "+str(rc),flush=True)

            # Subscribing in on_connect() means that if we lose the connection and
            # reconnect then subscriptions will be renewed.
            client.subscribe(self.mqtt_topic)

        def on_message(client, userdata, msg):
            #print(msg.topic+" "+str(msg.payload, "utf-8"),flush=True)
            shared_data = interpreter.interpret_message(str(msg.payload, "utf-8"))
            self.shared_data = smoother.smooth(shared_data)

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

        self.args = self.parser.parse_args()

        log_name = 'log/all.log'
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

        #Initialize threading
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
            t2 = threading.Thread(target = Simulation.phase_update_simulation, args = (self,"red",run_event))
        elif self.args.test == 3:
            t2 = threading.Thread(target = Simulation.phase_switch_simulation, args = (self,6,run_event))
        elif self.args.test == 4:
            t2 = threading.Thread(target = Simulation.phase_fast_simulation, args = (self,"green",run_event))
        elif self.args.test == 5:
            t2 = threading.Thread(target = Simulation.mqtt_client_simulation_dataframe, args = (self,None,run_event))
        elif self.args.test == 6:
            t2 = threading.Thread(target = Simulation.phase_switch_simulation, args = (self,30,run_event))            
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
