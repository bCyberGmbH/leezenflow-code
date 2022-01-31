import time

class HoersterTorSmoother():

    def __init__(self):
        self.hoerster_bias = 23 # Average number of seconds that remain after an anomaly
        self.detected_12 = False
        self.anomaly_detected = False
        self.anomaly_start_time = None
        self.anomaly_phase = None
        self.anomaly_time_threshold = 2.1
        self.anomaly_time_elapsed = 0
        self.bias = 3

    def smooth(self,shared_data):
        try:
            if not self.detected_12 and shared_data["remaining_time"] == 12.0:
                self.detected_12 = True
                self.anomaly_start_time = time.monotonic()

            if self.detected_12:
                self.anomaly_time_elapsed = time.monotonic() - self.anomaly_start_time

                if self.anomaly_time_elapsed >= self.anomaly_time_threshold and not self.anomaly_detected:
                    self.anomaly_detected = True
                    print("Anomaly detected")
                    self.anomaly_phase = shared_data["current_phase"]

                if self.anomaly_detected and self.anomaly_phase != shared_data["current_phase"]: # Phase has switched, resetting
                    self.anomaly_detected = False
                    self.detected_12 = False
                    return shared_data

                if self.anomaly_detected:
                    new_shared_data = {}
                    new_shared_data["current_phase"] = shared_data["current_phase"]
                    linear_remaining_time = self.hoerster_bias - self.anomaly_time_elapsed
                    new_shared_data["remaining_time"] = int(self.bias+linear_remaining_time/1.1**(self.anomaly_time_elapsed - self.anomaly_time_threshold)) # Not rounding will break row update
                    return new_shared_data

                if shared_data["remaining_time"] != 12.0:
                    self.detected_12 = False
                    return shared_data

                return shared_data
            else:
                return shared_data

        except Exception():
            print("Smoothing failed.",flush=True)
            return shared_data
