import time
import datetime
import xml.etree.ElementTree as ET

class StatisticsTool():

    def __init__(self):
        self.current_file = "log/phase_statistics_A.csv"
        self.filename1 = "log/phase_statistics_A.csv"
        self.filename2 = "log/phase_statistics_B.csv"
        self.flag_changed_today = False

    def add_to_csv(self, line):
        with open(self.current_file , "a", encoding='utf-8') as file_object:
            file_object.write(line)

    # Change the file at first day of month. The file older than one month is overwritten.
    def switch_file_name(self):
        day_of_month = datetime.datetime.now().day
        if day_of_month == 1 and not self.flag_changed_today:
            if self.current_file == self.filename1:
                self.current_file = self.filename2
            else:
                self.current_file = self.filename1
            self.reset_current_file()
            self.flag_changed_today = True

        if day_of_month > 1:
            self.flag_changed_today = False

    def reset_current_file(self):
        with open(self.current_file , "w", encoding='utf-8') as file_object:
            file_object.write("raspberry_timestamp,timestamp,minute_of_year,phase,likely_time_phase_change,remaining_phase_seconds") # Initialize csv header

    def save_message(self, message):
        try:
            tree = ET.ElementTree(ET.fromstring(message))
            root = tree.getroot()

            timestamp = int(root.find('spat/intersections/IntersectionState/timeStamp').text)
            moy = int(root.find('spat/intersections/IntersectionState/moy').text)
            likely_time = int(root.find('spat/intersections/IntersectionState/states/MovementState/state-time-speed/MovementEvent/timing/likelyTime').text)
            phase = root.find('spat/intersections/IntersectionState/states/MovementState/state-time-speed/MovementEvent/eventState')[0].tag

            # Clock: "hh : mm : ss" (e.g. 13:42:02)
            clock_minutes = moy % 60 # i.e. mm (e.g. 42)
            clock_seconds = timestamp / 1000 # i.e. ss (e.g. 02)

            if likely_time / 10 <= (moy % 60) * 60: # If true, likely_time corresponds to next hour
                remaining_minutes_of_current_hour = 60 - clock_minutes
                remaining_seconds_of_current_hour = 60 - clock_seconds
                remaining_seconds_of_the_next_hour = likely_time / 10
                remaining_phase_seconds = remaining_minutes_of_current_hour * 60 + remaining_seconds_of_current_hour + remaining_seconds_of_the_next_hour
            else: # likely_time corresponds to current hour
                predicted_seconds_of_hour = likely_time / 10
                current_seconds_of_hour = clock_minutes * 60 + clock_seconds
                remaining_phase_seconds = predicted_seconds_of_hour - current_seconds_of_hour

            raspberry_timestamp = time.time()

            line = f"{str(raspberry_timestamp)} {str(timestamp)} {str(moy)} {str(phase)} {str(likely_time)} {str(remaining_phase_seconds)}"
            self.add_to_csv(line)

            self.switch_file_name()

        except Exception:
            print("Statistic logging failed...")

