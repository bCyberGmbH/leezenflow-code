import argparse
import time
import sys
import os
import threading
import configparser
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))

#from leezenflow_display import LeezenflowDisplay

from message_interpreter import Interpreter
from simulations import Simulation
from shared_state import SharedState



class LeezenflowBase(object):

    def __init__(self, command_line_args, display):
        self.args = command_line_args
        self.display = display

    def receiver(self, mode, run_event):
        interpreter = Interpreter()

        # Modify incomming messages (e.g. to smooth values)
        if self.args.modifier == 1:
            from message_modifier import ModifierHoerstertor
            modify = ModifierHoerstertor().smooth
        else:
            print("No modifier selected.")
            modify = lambda x: x # Return value unchanged
 
        # Read config.ini
        try:    
            config = configparser.ConfigParser()
            config.read('config.ini')
        except KeyError:
            print("Configuration file or values within missing...")

        # Select SPATEM message receiver 
        if mode == "mqtt":
            from receivers.mqtt import MQTTReceiver
            client = MQTTReceiver(config=config, interpreter=interpreter, modify=modify)
            client.start()
            while run_event.is_set():
                client.loop()
        elif mode == "udp":
            from receivers.udp import UDPReceiver
            SharedState.interpreter = interpreter.interpret_message
            SharedState.modifier = modify
            client = UDPReceiver(config=config)
            client.run()
        else:
            print("No messages will be received. Use tests to simulate messages.")

    def process(self):

        # Initialize threading
        run_event = threading.Event()
        run_event.set()

        # Thread for animation
        t1 = threading.Thread(target = self.run, args = (None,run_event))

        # Select receiver
        if self.args.receiver == 0:
            pass
        elif self.args.receiver == 1:
            t2 = threading.Thread(target = self.receiver(mode="mqtt"), args = (None,run_event))
        elif self.args.receiver == 2:
            t2 = threading.Thread(target = self.receiver, args = ("udp",run_event))
        else:
            raise Exception("Invalid receiver argument.")

        # Select test mode 
        if self.args.test == -1:
            pass
        elif self.args.test == 0:
            t2 = threading.Thread(target = Simulation.phase_switch_simulation_4_phases, args = (5,run_event))
        elif self.args.test == 1:
            t2 = threading.Thread(target = Simulation.mqtt_log, args = (None,run_event))
        elif self.args.test == 2:
            t2 = threading.Thread(target = Simulation.log_simulation, args = (None,run_event))
        elif self.args.test == 3:
            t2 = threading.Thread(target = Simulation.phase_switch_simulation, args = (5,run_event))
        elif self.args.test == 4:
            t2 = threading.Thread(target = Simulation.phase_switch_simulation, args = (30,run_event))
        elif self.args.test == 5:
            t2 = threading.Thread(target = Simulation.phase_update_simulation, args = ("red",run_event))
        elif self.args.test == 6:
            t2 = threading.Thread(target = Simulation.phase_fast_simulation, args = ("green",run_event))
        elif self.args.test == 7:
            t2 = threading.Thread(target = Simulation.stale_prediction, args = (None,run_event))
        elif self.args.test == 8:
            t2 = threading.Thread(target = Simulation.log_simulation, args = (None,run_event))
        else:
            raise Exception("Invalid test argument.")

        # Start threads
        print("Press CTRL-C to stop leezenflow")
        t1.start()
        try:
            t2.start()
        except UnboundLocalError:
            print("Cannot run without either test dataset or receiver. Use flag --test 0 to run with test dataset 0.")

        try:
            while True:
                time.sleep(.1)
        except KeyboardInterrupt:
            print("Attempting to close threads...")
            run_event.clear()
            t1.join()
            t2.join()
            print ("Threads successfully closed.")

        return True
