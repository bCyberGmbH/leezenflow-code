import time

from leezenflow_base import LeezenflowBase

from shared_state import SharedState
from command_line_args import CommandLineArgs

class AnimationManuYellow(LeezenflowBase):
    
    def __init__(self, command_line_args, display):
        super(AnimationManuYellow, self).__init__(command_line_args, display)

        self.display = display

        self.bike_height = None
        self.bike1_position = None
        self.bike2_position = None
        self.time_elapsed_bike = None

        self.last_bike_time = None
        self.bike_still_moving = False

        self.update_interval = 0.01
        self.matrix_height = 96              
        self.max_white = 255 # Maximum brightness of the white bike

        self.bike_box_height = 23
        self.bike_height = 8
        self.bike_center = 8

        self.color_green = (0,255,132)
        self.color_red = (255,49,73)
        self.color_yellow = (255,255,0)
        self.placeholder_time_for_short_phases = 45

        self.last_update_current_row = None
        self.last_update_prediction_sec = None
        self.last_update_elapsed_sec = None
        self.last_update_elapsed_time_start = None

        # variables manu
        self.lastGreenPhaseTime = -1
        self.averageGreenPhaseTime = -1
        self.greenPhaseArray = []
        self.greenPhasesToSave = 10
        self.greenPhaseCounter = -1
        self.lastRedPhaseTime = -1
        self.averageRedPhaseTime = -1
        self.redPhaseArray = []
        self.redPhasesToSave = 10
        self.redPhaseCounter = -1
        self.firstRun = True
        self.testThreadStarted = False
        self.switchedPhase = False
        self.starttime = time.time()
        self.seconds_to_reach_traffic_light = 0
        self.seconds_to_reach_traffic_light_at_yellow = 0
        self.yellow_red_seconds_difference = 0
        self.bicycle_speed = 0 # in m/s
        self.bicycle_yellow_speed = 0 # in m/s
        self.distance = 0
        self.first_initialize = True
        self.eary_switch_current_phase = None

        #self.display = Display()

    def run(self,_,run_event):

        g1,g2,g3 = *self.color_green,
        r1,r2,r3 = *self.color_red,
        y1,y2,y3 = *self.color_yellow,


        def calculate_seconds_to_reach_traffic_light():
            # time = distance (in meter) / speed (in m/s)
            self.bicycle_speed = CommandLineArgs.command_line_args.bicycle_speed / 3.6 # calculate km/h to m/s
            self.bicycle_yellow_speed = CommandLineArgs.command_line_args.bicycle_yellow_speed / 3.6
            self.distance = CommandLineArgs.command_line_args.distance
            if (self.distance > 0 and self.bicycle_speed > 0):
                self.seconds_to_reach_traffic_light = self.distance / self.bicycle_speed
                if (self.bicycle_yellow_speed > 0):
                    self.seconds_to_reach_traffic_light_at_yellow = self.distance / self.bicycle_yellow_speed
                    self.yellow_red_seconds_difference = self.seconds_to_reach_traffic_light - self.seconds_to_reach_traffic_light_at_yellow

        calculate_seconds_to_reach_traffic_light()

        def update_current_row():
            if self.last_update_prediction_sec <= 0.1:
                #print("Prediction <= 0.1", flush=True)
                return self.matrix_height
            self.current_row = self.last_update_current_row + int(((self.matrix_height - self.last_update_current_row) / self.last_update_prediction_sec) * self.last_update_elapsed_sec)

        def process_predict_update_early_switch(phase):
            self.last_update_elapsed_time_start = time.monotonic()

            self.current_row = self.bike_box_height
            self.last_update_current_row = self.current_row
            self.last_update_elapsed_sec = 0
            average_phase_time = 0
            
            if phase == "red":
                if len(self.redPhaseArray) > 3:
                    average_phase_time = self.averageRedPhaseTime
                else:
                    average_phase_time = 50
            else:
                if len(self.greenPhaseArray) > 3:
                    average_phase_time = self.averageGreenPhaseTime
                else:
                    average_phase_time = 50

            # ToDo Placeholder
            # ToDo Placeholder
            # ToDo Placeholder
            # ToDo Placeholder
            # ToDo Placeholder
            # ToDo Placeholder
            
            # ToDo Placeholder
            # ToDo Placeholder
            # ToDo Placeholder
            # ToDo Placeholder
            # ToDo Placeholder
            # ToDo Placeholder

            #self.last_update_prediction_sec = max(0, average_phase_time + ((self.seconds_to_reach_traffic_light * 2) + self.yellow_red_seconds_difference))
            if phase == "yellow":
                self.last_update_prediction_sec = max(0, self.yellow_red_seconds_difference)
            elif  phase == "green":
                self.last_update_prediction_sec = max(0, average_phase_time + self.seconds_to_reach_traffic_light)
            else:
                self.last_update_prediction_sec = max(0, average_phase_time + (self.seconds_to_reach_traffic_light - self.yellow_red_seconds_difference)) # early red


        def process_prediction_update_green_phase():
            self.last_update_current_row = self.current_row
            self.last_update_elapsed_sec = 0
            if SharedState.shared_data["current_phase"] == "yellow" or SharedState.shared_data["current_phase"] == "red-yellow":
                self.last_update_prediction_sec = self.placeholder_time_for_short_phases
            else:
                #self.last_update_prediction_sec = max(0, (SharedState.shared_data["change_timestamp"] - SharedState.shared_data["current_timestamp"]) - round(self.seconds_to_reach_traffic_light - self.yellow_red_seconds_difference))
                self.last_update_prediction_sec = max(0, (SharedState.shared_data["change_timestamp"] - SharedState.shared_data["current_timestamp"]) - self.seconds_to_reach_traffic_light) # ToDo - hierdurch switch die ampel jetzt erst 14 sekunden vorher um statt 18. Die 4 sekunden differenz müssen dann die gelbphase sein. Darf aber nicht bei rot->grün benutzt werden
            self.last_update_elapsed_time_start = time.monotonic()

        def process_prediction_update_red_phase():
            self.last_update_current_row = self.current_row
            self.last_update_elapsed_sec = 0
            if SharedState.shared_data["current_phase"] == "yellow" or SharedState.shared_data["current_phase"] == "red-yellow":
                self.last_update_prediction_sec = self.placeholder_time_for_short_phases
            else:
                #self.last_update_prediction_sec = max(0, (SharedState.shared_data["change_timestamp"] - SharedState.shared_data["current_timestamp"]) - (self.seconds_to_reach_traffic_light - self.yellow_red_seconds_difference))
                self.last_update_prediction_sec = max(0, (SharedState.shared_data["change_timestamp"] - SharedState.shared_data["current_timestamp"]) - self.seconds_to_reach_traffic_light )
            self.last_update_elapsed_time_start = time.monotonic()

        def get_next_bike_step(time_elapsed_bike,last_bike_time):
            if time_elapsed_bike > last_bike_time + 0.05:
                self.last_bike_time = self.time_elapsed_bike
                return True

        def move_bikes_green(move_pixel_amount):
            self.display.draw_bike(self.max_white, self.max_white, self.max_white ,self.bike_height,self.bike1_position,moving=True)
            if get_next_bike_step(self.time_elapsed_bike,self.last_bike_time): 
                self.bike1_position += move_pixel_amount 
                self.bike2_position += move_pixel_amount
            if self.bike1_position >= 37: 
                self.bike1_position = -20
                self.bike2_position = 37
            if self.bike2_position >= 37:
                self.display.draw_bike(self.max_white, self.max_white, self.max_white ,self.bike_height,self.bike2_position,moving=True)
                if self.bike2_position >= 45:
                    self.bike2_position = -999

        def move_bike_red():
            self.display.draw_bike(self.max_white, self.max_white, self.max_white ,self.bike_height,self.bike1_position,moving=True)
            if get_next_bike_step(self.time_elapsed_bike,self.last_bike_time): 
                self.bike1_position += 1
            if self.bike1_position >= 45: # If the bike's position is beyond the center, the bike leaves the matrix and respawns in the center
                self.bike1_position = -20
                self.bike_still_moving = False
            if self.bike1_position == 8+1: # If the bike's position is before the center, the bike drives until the center is reached 
                self.bike_still_moving = False

        def initialize_phase_variables():
            # Time for rows
            self.last_update_elapsed_time_start = time.monotonic()
            self.last_update_elapsed_time = 0

            # Time for bikes
            self.start_time_bike = time.monotonic()
            self.time_elapsed_bike = 0

            # self.last_update_prediction_sec = max(0, (SharedState.shared_data["change_timestamp"] - SharedState.shared_data["current_timestamp"]) - 10)
            #self.last_update_prediction_sec = max(0, (SharedState.shared_data["change_timestamp"] - SharedState.shared_data["current_timestamp"]) - (self.seconds_to_reach_traffic_light - self.yellow_red_seconds_difference))
            self.last_update_prediction_sec = max(0, (SharedState.shared_data["change_timestamp"] - SharedState.shared_data["current_timestamp"]) - self.seconds_to_reach_traffic_light)
            self.last_message = None
            if self.first_initialize == True:
                self.current_row = self.bike_box_height
                self.first_initialize = False
            self.last_update_current_row = self.current_row

        ### Start the loop ###
        while(run_event.is_set()):

            ## Green phase ##
            if SharedState.shared_data["current_phase"] == "green" or SharedState.shared_data["current_phase"] == "red-yellow":
                # There are two bikes such that the second bike can roll into the matrix before the other has left 
                self.last_bike_time = 0.0
                self.bike1_position = 8 
                self.bike2_position = -999
                self.bike_still_moving = True

                self.switchedPhase = False

                initialize_phase_variables()

                eary_switch_current_phase = "green"

                if self.firstRun == True:
                    self.firstRun = False
                    self.display.draw_rectangle(self.bike_box_height,self.matrix_height, g1, g2, g3) # pure green
    
                while(self.current_row < self.matrix_height) and run_event.is_set():

                    self.time_elapsed_bike = time.monotonic() - self.start_time_bike
                    self.last_update_elapsed_sec = time.monotonic() - self.last_update_elapsed_time_start

                    update_current_row()
                    self.display.draw_black_trend_rectangle(0,self.current_row, g1, g2, g3) # Black fade and resetting of bike box
                    move_bikes_green(1)

                    if SharedState.shared_data["hash"] != self.last_message: # This avoids updates with every message that would break animation. Problematic with additional info in shared data.    
                        if SharedState.shared_data["current_phase"] != "green" and SharedState.shared_data["current_phase"] != "red-yellow":
                            break
                        process_prediction_update_green_phase()
                        # process_prediction_update_yellow_phase()

                        self.display.draw_rectangle(self.bike_box_height+self.current_row,self.matrix_height, g1, g2, g3) # pure green
                        self.last_message = SharedState.shared_data["hash"]

                        if SharedState.shared_data["current_phase"] == "green":
                            # ToDo -->
                            self.lastGreenPhaseTime = max(0, SharedState.shared_data["change_timestamp"] - SharedState.shared_data["current_timestamp"])
                            if len(self.greenPhaseArray) >= self.greenPhasesToSave:
                                self.greenPhaseArray.pop(0)
                            self.greenPhaseArray.append(self.lastGreenPhaseTime)
                            self.averageGreenPhaseTime = 0
                            for x in self.greenPhaseArray:
                                self.averageGreenPhaseTime += x
                            self.averageGreenPhaseTime = self.averageGreenPhaseTime / len(self.greenPhaseArray)
                            # <-- ToDo

                    time.sleep(self.update_interval)

                self.switchedPhase = True
                #self.current_row = self.bike_box_height
                #process_predict_update_early_switch()
                just_switched = True

                while SharedState.shared_data["current_phase"] == "green" and (self.current_row >= self.matrix_height) and run_event.is_set():

                    if eary_switch_current_phase == "green":
                        # erst 4s voll gelb

                        self.current_row = self.bike_box_height
                        self.display.draw_rectangle(self.bike_box_height,self.matrix_height, y1, y2, y3) # pure yellow
                        process_predict_update_early_switch("yellow")

                        while eary_switch_current_phase == "green":
                            if self.current_row >= self.matrix_height:
                                eary_switch_current_phase = "yellow"
                            else:
                                self.time_elapsed_bike = time.monotonic() - self.start_time_bike
                                self.last_update_elapsed_sec = time.monotonic() - self.last_update_elapsed_time_start


                                update_current_row()
                                #self.display.draw_black_trend_rectangle(0,self.current_row, r1, r2, r3) # Black fade and resetting of bike box
                                self.display.draw_black_trend_rectangle(0,self.current_row, y1, y2, y3) # Black fade and resetting of bike box
                                move_bikes_green(2)

                                # if self.bike_still_moving:
                                #     self.display.draw_black_trend_rectangle(0,self.current_row, r1, r2, r3) # Black fade
                                #     move_bike_red()
                                # else:
                                #     self.display.draw_bike(self.max_white, self.max_white, self.max_white ,self.bike_height,self.bike_center)

                                time.sleep(self.update_interval)
                    else:
                        # dann 14s + avgRedTime s voll rot

                        self.current_row = self.bike_box_height
                        self.display.draw_rectangle(self.bike_box_height,self.matrix_height, r1, r2, r3) # pure red
                        process_predict_update_early_switch("red")

                        while SharedState.shared_data["current_phase"] == "green":
                            self.time_elapsed_bike = time.monotonic() - self.start_time_bike
                            self.last_update_elapsed_sec = time.monotonic() - self.last_update_elapsed_time_start


                            update_current_row()
                            #self.display.draw_black_trend_rectangle(0,self.current_row, r1, r2, r3) # Black fade and resetting of bike box
                            self.display.draw_black_trend_rectangle(0,self.current_row, r1, r2, r3) # Black fade and resetting of bike box
                            #move_bikes_green(2)

                            if self.bike_still_moving:
                                self.display.draw_black_trend_rectangle(0,self.current_row, r1, r2, r3) # Black fade
                                move_bike_red()
                            else:
                                self.display.draw_bike(self.max_white, self.max_white, self.max_white ,self.bike_height,self.bike_center)

                            time.sleep(self.update_interval)

                # Wait until there is a message that the phase has actually changed
                time_wait = time.monotonic()
                while SharedState.shared_data["current_phase"] == "green" and run_event.is_set():
                    # Continue to move bikes
                    self.display.draw_rectangle_shade(0,self.matrix_height, g1, g2, g3) # Just to reset each bike frame 
                    move_bikes_green(1)
                    self.time_elapsed_bike = time.monotonic() - self.start_time_bike

                    time.sleep(self.update_interval)
                    if time.monotonic() >= time_wait + 60: # 60 sec w/o expected phase change
                        #print("Green phase prediction time ended 60s ago, however no red phase message was received. Leaving green state...",flush=True)
                        self.display.Fill(0,0,0)
                        SharedState.shared_data["current_phase"] = "awaiting_message"
                        break

            ## Red phase ##  
            elif SharedState.shared_data["current_phase"] == "red" or SharedState.shared_data["current_phase"] == "yellow":

                initialize_phase_variables()
                eary_switch_current_phase = "red"
                just_switched = True

                self.switchedPhase = False

                # Red phase while bike moving. The bike moves beyond the green phase until it is in centered position.
                self.last_bike_time = 0.0

                if self.firstRun == True:
                    self.firstRun = False
                    self.display.draw_rectangle(self.bike_box_height,self.matrix_height, r1, r2, r3) # Red
                    
                while((self.current_row < self.matrix_height) and run_event.is_set()):
                    self.time_elapsed_bike = time.monotonic() - self.start_time_bike
                    self.last_update_elapsed_sec = time.monotonic() - self.last_update_elapsed_time_start
                    
                    update_current_row()

                    if self.bike_still_moving:
                        self.display.draw_black_trend_rectangle(0,self.current_row, r1, r2, r3) # Black fade
                        move_bike_red()
                    else:
                        if just_switched:
                            self.display.draw_rectangle_shade(0,self.bike_box_height, r1, r2, r3) # Reset bottom bike box to shaded red
                            self.display.draw_bike(self.max_white, self.max_white, self.max_white ,self.bike_height,self.bike_center)
                            just_switched = False
                        self.display.draw_black_trend_rectangle(self.bike_box_height,self.current_row, r1, r2, r3) # Black fade

                    if SharedState.shared_data["hash"] != self.last_message: # This avoids updates with every message that would break animation. Problematic with additional info in shared data.
                        if SharedState.shared_data["current_phase"] != "red" and SharedState.shared_data["current_phase"] !="yellow":
                            break
                        process_prediction_update_red_phase()
                        self.display.draw_rectangle(self.bike_box_height+self.current_row,self.matrix_height, r1, r2, r3) # pure red
                        self.last_message = SharedState.shared_data["hash"]

                        if SharedState.shared_data["current_phase"] == "red":
                            # ToDo -->
                            self.lastRedPhaseTime = max(0, SharedState.shared_data["change_timestamp"] - SharedState.shared_data["current_timestamp"])
                            if len(self.redPhaseArray) >= self.redPhasesToSave:
                                self.redPhaseArray.pop(0)
                            self.redPhaseArray.append(self.lastRedPhaseTime)
                            self.averageRedPhaseTime = 0
                            for x in self.redPhaseArray:
                                self.averageRedPhaseTime += x
                            self.averageRedPhaseTime = self.averageRedPhaseTime / len(self.redPhaseArray)
                            # <-- ToDo

                    time.sleep(self.update_interval)

                self.switchedPhase = True
                while SharedState.shared_data["current_phase"] == "red" and (self.current_row >= self.matrix_height) and run_event.is_set():
                    self.current_row = self.bike_box_height
                    self.display.draw_rectangle(self.bike_box_height,self.matrix_height, g1, g2, g3) # pure green
                    process_predict_update_early_switch("green")

                    while SharedState.shared_data["current_phase"] == "red":
                        self.time_elapsed_bike = time.monotonic() - self.start_time_bike
                        self.last_update_elapsed_sec = time.monotonic() - self.last_update_elapsed_time_start
                        #self.display.draw_black_trend_rectangle(0,self.current_row, g1, g2, g3) # Black fade and resetting of bike box
                        update_current_row()
                        self.display.draw_black_trend_rectangle(0,self.current_row, g1, g2, g3) # Black fade and resetting of bike box
                        move_bikes_green(1)
                        
                        time.sleep(self.update_interval)



                # Wait until there is a message that the phase has actually changed
                time_wait = time.monotonic()
                while SharedState.shared_data["current_phase"] == "red" and run_event.is_set():
                    time.sleep(0.1)
                    if time.monotonic() >= time_wait + 60: # 60 sec w/o expected phase change
                        #print("Red phase prediction time ended 10s ago, however no green phase message was received. Leaving red state...",flush=True)
                        self.display.Fill(0,0,0)
                        SharedState.shared_data["current_phase"] = "awaiting_message"
                        break

            elif SharedState.shared_data["current_phase"] == "awaiting_message":
                time_wait = time.monotonic()
                print("Awaiting message...",flush=True)
                pulse = 255
                down = True
                while SharedState.shared_data["current_phase"] == "awaiting_message" and run_event.is_set():
                    time.sleep(0.1)
                    self.display.draw_bike(pulse, pulse, pulse, self.bike_height, self.bike_center)
                    if down:
                        pulse -= 10
                        if pulse <= 0:
                            pulse = 0
                            down = False
                    else:
                        pulse +=10
                        if pulse >= 255:
                            pulse = 255
                            down = True
                    if time.monotonic() >= time_wait + 600: # After 10 min
                        self.display.draw_rectangle(0,self.matrix_height,0,0,0)
                        self.display.SetPixel(1, 1, 10, 10, 10)
                        while SharedState.shared_data["current_phase"] == "awaiting_message" and run_event.is_set():
                            time.sleep(1)
            else:
                print("Unknown phase / error: ",SharedState.shared_data,flush=True)
                self.display.draw_bike(255, 49, 73, self.bike_height, self.bike_center)
                time.sleep(15)
                print("Trying again...",flush=True)
    
