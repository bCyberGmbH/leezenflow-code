import xml.etree.ElementTree as ET

class Interpreter():
    def __init__(self):
        self.placeholder_time_for_short_phases = 45

    def interpret_message(self,message):
        try:
            tree = ET.ElementTree(ET.fromstring(message))
            root = tree.getroot()

            time_stamp = int(root.find('spat/intersections/IntersectionState/timeStamp').text)
            moy = int(root.find('spat/intersections/IntersectionState/moy').text)
            likely_time = int(root.find('spat/intersections/IntersectionState/states/MovementState/state-time-speed/MovementEvent/timing/likelyTime').text)
            ending_phase = root.find('spat/intersections/IntersectionState/states/MovementState/state-time-speed/MovementEvent/eventState')[0].tag

            #print("Interpreter:",time_stamp,moy,likely_time,ending_phase)

            if ending_phase == "pre-Movement": #red-yellow
                current_phase = "green"
                remaining_time = self.placeholder_time_for_short_phases
            elif ending_phase == 'permissive-clearance': #yellow
                current_phase = "red"
                remaining_time = self.placeholder_time_for_short_phases
            else:        
                if ending_phase == 'permissive-Movement-Allowed': #green
                    current_phase = "green"
                elif ending_phase == 'stop-And-Remain': #red
                    current_phase = "red"
                else:
                    current_phase = "unknown_phase_error"

                if likely_time / 10 + 3 <= (moy % 60) * 60: # Here, it's ok to have a >= -3 prediction; -1 observed in log3
                    remaining_time = (60000 - time_stamp) / 1000 + likely_time / 10
                else:
                    remaining_time = likely_time / 10 - (moy % 60) * 60 - time_stamp / 1000

            return {
                    "current_phase" : current_phase,
                    "remaining_time" : remaining_time,
                    "prediction_absolute": likely_time
                    }
        except Exception as e:
                return {
                        "current_phase" : "Interpretation error",
                        "exception": e,
                        "message": message
                        }

# "variables:" :  [current_phase,ending_phase,remaining_time,likely_time,time_stamp,moy]
