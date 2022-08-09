import time
from xml.etree.ElementTree import ParseError
import xml.etree.ElementTree as ET

class Interpreter():
    def __init__(self):
        self.state = {
                "current_phase" : "red",
                "current_timestamp" : 0,
                "change_timestamp" : 10,
                "hash" : 0
            }
    def interpret_message(self,message):
        try:
            tree = ET.ElementTree(ET.fromstring(message))
            root = tree.getroot()

            if root.tag == "SPATEM":
                time_stamp = int(root.find('spat/intersections/IntersectionState/timeStamp').text)
                moy = int(root.find('spat/intersections/IntersectionState/moy').text)
                likely_time = int(root.find('spat/intersections/IntersectionState/states/MovementState/state-time-speed/MovementEvent/timing/likelyTime').text)
                phase = root.find('spat/intersections/IntersectionState/states/MovementState/state-time-speed/MovementEvent/eventState')[0].tag

                hash_ = hash(str(likely_time) + phase)

                # likely_time is the 1/10 seconds of the current or (edge case) following hour 
                # time_stamp is the seconds of the minute + "000" (e.g. 25000 = 25s)

                # print("Interpreter:",time_stamp,moy,likely_time,phase)

                if phase == "pre-Movement": # red + yellow (when a red phase ends)
                    current_phase = "red-yellow"
                elif phase == "permissive-clearance": # yellow
                    current_phase = "yellow"      
                elif phase == 'permissive-Movement-Allowed': # green
                    current_phase = "green"
                elif phase == 'stop-And-Remain': # red
                    current_phase = "red"
                else:
                    current_phase = "unknown_phase_error"
                
                # Clock: "hh : mm : ss" (e.g. 13:42:02)
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

                self.state = {
                    "current_phase" : current_phase,
                    "current_timestamp" : current_timestamp,
                    "change_timestamp" : current_timestamp + remaining_phase_seconds,
                    "hash" : hash_ # Can be used to check whether the prediction has changed
                }
                return self.state
        except ParseError:
            # print("Probably received malformated MAPEM, returning last recoreded state...")
            return self.state
        except Exception as e:
                return {
                    "current_phase" : "Interpretation error",
                    "exception": e,
                    "message": message,
                    "hash" : 0
                }
