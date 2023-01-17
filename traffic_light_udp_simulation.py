import io
import re
import socket
import sys
import time
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError

UDP_IP = "0.0.0.0"
#UDP_IP = "10.0.0.2"
UDP_PORT = 9977
MESSAGE1 = "GREEN"
MESSAGE2 = "RED"

LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'

print("UDP target IP:", UDP_IP)
print("UDP target port:", UDP_PORT)

with io.open('sample_messages/august1.log','r',encoding='utf8') as f:
    text = f.read()

spat_xml = re.findall('[\s\S]*?</SPATEM>', text)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

color = "32"

def interpret_confidence(confidence):
    if confidence == 0:
        return "21% probability"
    elif confidence == 1:
        return "36% probability"
    elif confidence == 2:
        return "47% probability"
    elif confidence == 3:
        return "56% probability"
    elif confidence == 4:
        return "62% probability"
    elif confidence == 5:
        return "68% probability"
    elif confidence == 6:
        return "73% probability"
    elif confidence == 7:
        return "77% probability"
    elif confidence == 8:
        return "81% probability"
    elif confidence == 9:
        return "85% probability"
    elif confidence == 10:
        return "88% probability"
    elif confidence == 11:
        return "91% probability"
    elif confidence == 12:
        return "94% probability"
    elif confidence == 13:
        return "96% probability"
    elif confidence == 14:
        return "98% probability"
    elif confidence == 15:
        return "100% probability"
    else:
        return "unknown"

def interpret_phase(phase):
    global color
    global inactive_color
    traffic_light_active = f"\033[1;{color}m\u2B24\033[0;0m"

    if phase == "pre-Movement": # red + yellow (when a red phase ends)
        color = "31" # red
        print(traffic_light_active)
        print(f"\033[1;33m()\033[0;0m")
        print(f"\033[1;32m()\033[0;0m")
        return "red-yellow"
    elif phase == "permissive-clearance": # yellow
        color = "33" # yellow
        print(f"\033[1;31m()\033[0;0m")
        print(traffic_light_active)
        print(f"\033[1;32m()\033[0;0m")
        return "yellow"
    elif phase == 'permissive-Movement-Allowed': # green
        color = "32" # green
        print(f"\033[1;31m()\033[0;0m")
        print(f"\033[1;33m()\033[0;0m")
        print(traffic_light_active)
        return "green"
    elif phase == 'stop-And-Remain': # red
        color = "31" # red
        print(traffic_light_active)
        print(f"\033[1;33m()\033[0;0m")
        print(f"\033[1;32m()\033[0;0m")
        return "red"
    else:
        return "unknown_phase_error"

for spatem_xml in spat_xml: 
    tree = ET.ElementTree(ET.fromstring(spatem_xml))
    root = tree.getroot()

    phase = root.find('spat/intersections/IntersectionState/states/MovementState/state-time-speed/MovementEvent/eventState')[0].tag
    time_stamp = int(root.find('spat/intersections/IntersectionState/timeStamp').text)
    moy = int(root.find('spat/intersections/IntersectionState/moy').text)
    likely_time = int(root.find('spat/intersections/IntersectionState/states/MovementState/state-time-speed/MovementEvent/timing/likelyTime').text)
    confidence = int(root.find('spat/intersections/IntersectionState/states/MovementState/state-time-speed/MovementEvent/timing/confidence').text)

    clock_minutes = moy % 60 # i.e. mm (e.g. 42)
    clock_seconds = time_stamp / 1000 # i.e. ss (e.g. 02)

    if likely_time / 10 <= (moy % 60) * 60: # If true, likely_time corresponds to next hour
        remaining_minutes_of_current_hour = 60 - clock_minutes
        remaining_seconds_of_current_hour = 60 - clock_seconds
        remaining_seconds_of_the_next_hour = likely_time / 10
        remaining_phase_seconds = remaining_minutes_of_current_hour * 60 + remaining_seconds_of_current_hour + remaining_seconds_of_the_next_hour
    else: # likely_time corresponds to current hour
        predicted_seconds_of_hour = likely_time / 10
        current_seconds_of_hour = clock_minutes * 60 + clock_seconds
        remaining_phase_seconds = predicted_seconds_of_hour - current_seconds_of_hour

    current_timestamp = time.monotonic()

    print(LINE_UP, end=LINE_CLEAR)
    print(LINE_UP, end=LINE_CLEAR)
    print(LINE_UP, end=LINE_CLEAR)
    print(LINE_UP, end=LINE_CLEAR)
    print(LINE_UP, end=LINE_CLEAR)
    print(LINE_UP, end=LINE_CLEAR)

    interpret_phase(phase)

    print("------")
    print("remaining phase seconds:", remaining_phase_seconds)
    print("confidence:", interpret_confidence(confidence))

    sock.sendto(bytes(spatem_xml, "utf-8"), (UDP_IP, UDP_PORT))

    time.sleep(0.1)
