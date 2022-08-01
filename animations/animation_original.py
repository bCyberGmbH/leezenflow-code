from rgbmatrix import graphics
import time

from leezenflow_base import LeezenflowBase
from shared_state import SharedState

class AnimationOrignal(LeezenflowBase):
    def __init__(self, command_line_args):
        super(AnimationOrignal, self).__init__(command_line_args)

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
        self.length_shade = 25
        self.bias = 3
        self.placeholder_time_for_short_phases = 45

        self.last_update_current_row = None
        self.last_update_prediction_sec = None
        self.last_update_elapsed_sec = None
        self.last_update_elapsed_time_start = None
       
    def run(self,_,run_event):

        g1,g2,g3 = *self.color_green,
        r1,r2,r3 = *self.color_red,
        canvas = self.matrix

        def setRow(row_nr):
            for pixel in range(0,32):
                self.matrix.SetPixel(row_nr, pixel, 0, 0, 0)

        def draw_rectangle(y1,y2,r,g,b):
            for row in range(y1,y2):
                for pixel in range(0,32):
                    self.matrix.SetPixel(row, pixel, r, g, b)

        def draw_rectangle_shade(y1,y2,r,g,b):
            shade_intensity = self.length_shade *2
            for row in range(y1,y2):
                for pixel in range(0,32):
                    self.matrix.SetPixel(row, pixel, r/shade_intensity, g/shade_intensity, b/shade_intensity)

        def draw_black_trend_rectangle(y1,y2,r,g,b):
            y2 -= self.bias
            length = self.length_shade # How many shaded pixel?
            r1 = r/length
            g1 = g/length
            b1 = b/length

            for row in range(0,length): # Fade of length 25 upwards starting at y2
                for pixel in range(0,32):
                    self.matrix.SetPixel(y2+row, pixel, r1*(row+1), g1*(row+1), b1*(row+1))

            for row in range(y1,y2): # Plain dark green/red at the bottom
                for pixel in range(0,32):
                    self.matrix.SetPixel(row, pixel, r1/2, g1/2, b1/2) # Dark green/red

        # Function to manually draw a bike. It should also be possible (regarding performance) to include a .png graphic instead.
        def draw_bike(color,y_position,axis_x_left,moving=False):
            axis_x_left = axis_x_left
            axis_y = y_position
            axis_x_middle = axis_x_left + 7
            axis_x_right = axis_x_left + 15
            radius = 5

            # Wheels
            graphics.DrawCircle(canvas, axis_y, axis_x_left, radius, color)
            graphics.DrawCircle(canvas, axis_y, axis_x_right, radius, color)

            if moving:    
                # Speed lines
                graphics.DrawLine(canvas, axis_y-radius+1, axis_x_left-radius-7, axis_y-radius+1, axis_x_left-radius-1, color)
                graphics.DrawLine(canvas, axis_y-radius+4, axis_x_left-radius-4, axis_y-radius+4, axis_x_left-radius-2, color)
                graphics.DrawLine(canvas, axis_y-radius+8, axis_x_left-radius-6, axis_y-radius+8, axis_x_left-radius-2, color)

            graphics.DrawLine(canvas, axis_y, axis_x_left, axis_y, axis_x_middle, color)
            graphics.DrawLine(canvas, axis_y, axis_x_left, axis_y+8, axis_x_left+4, color)
            graphics.DrawLine(canvas, axis_y, axis_x_middle, axis_y+8,  axis_x_middle+4, color)
            graphics.DrawLine(canvas, axis_y+8, axis_x_left+4, axis_y+8,  axis_x_middle+4, color)
            graphics.DrawLine(canvas, axis_y, axis_x_right, axis_y+8, axis_x_right-4, color)
            graphics.DrawLine(canvas, axis_y+8,  axis_x_middle+4, axis_y+10,  axis_x_middle+5, color)
            graphics.DrawLine(canvas, axis_y+10,  axis_x_middle+5, axis_y+10,  axis_x_middle+7, color)
            graphics.DrawLine(canvas, axis_y+9, axis_x_left+4, axis_y+10,  axis_x_left+3, color)
            graphics.DrawLine(canvas, axis_y+11,  axis_x_left+1, axis_y+11,  axis_x_left+5, color)
          
        def update_current_row():
            if self.last_update_prediction_sec <= 0.1:
                print("Prediction <= 0.1", flush=True)
                return self.matrix_height
            self.current_row = self.last_update_current_row + int(((self.matrix_height - self.last_update_current_row) / self.last_update_prediction_sec) * self.last_update_elapsed_sec)

        def process_prediction_update():
            self.last_update_current_row = self.current_row
            self.last_update_elapsed_sec = 0
            if SharedState.shared_data["current_phase"] == "yellow" or SharedState.shared_data["current_phase"] == "red-yellow":
                self.last_update_prediction_sec = self.placeholder_time_for_short_phases
            else:
                self.last_update_prediction_sec = max(0, SharedState.shared_data["change_timestamp"] - SharedState.shared_data["current_timestamp"])
            self.last_update_elapsed_time_start = time.monotonic()

        def get_next_bike_step(time_elapsed_bike,last_bike_time):
            if time_elapsed_bike > last_bike_time + 0.05:
                self.last_bike_time = self.time_elapsed_bike
                return True

        def move_bikes_green():
            draw_bike(graphics.Color(self.max_white, self.max_white, self.max_white),self.bike_height,self.bike1_position,moving=True)
            if get_next_bike_step(self.time_elapsed_bike,self.last_bike_time): 
                self.bike1_position += 1 
                self.bike2_position += 1           
            if self.bike1_position >= 37: 
                self.bike1_position = -20
                self.bike2_position = 37
            if self.bike2_position >= 37:
                draw_bike(graphics.Color(self.max_white, self.max_white, self.max_white),self.bike_height,self.bike2_position,moving=True)
                if self.bike2_position >= 45:
                    self.bike2_position = -999       

        def move_bike_red():
            draw_bike(graphics.Color(self.max_white, self.max_white, self.max_white),self.bike_height,self.bike1_position,moving=True)
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

            self.last_update_prediction_sec = max(0, SharedState.shared_data["change_timestamp"] - SharedState.shared_data["current_timestamp"])
            self.last_message = None
            self.current_row = self.bike_box_height
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

                initialize_phase_variables()
                draw_rectangle(self.bike_box_height,self.matrix_height,g1,g2,g3) # pure green

                while(self.current_row < self.matrix_height) and run_event.is_set():
                    self.time_elapsed_bike = time.monotonic() - self.start_time_bike
                    self.last_update_elapsed_sec = time.monotonic() - self.last_update_elapsed_time_start

                    update_current_row()
                    draw_black_trend_rectangle(0,self.current_row,g1,g2,g3) # Black fade and resetting of bike box
                    move_bikes_green()

                    if SharedState.shared_data["hash"] != self.last_message: # This avoids updates with every message that would break animation. Problematic with additional info in shared data.    
                        if SharedState.shared_data["current_phase"] != "green" and SharedState.shared_data["current_phase"] != "red-yellow":
                            break
                        process_prediction_update()
                        draw_rectangle(self.bike_box_height+self.current_row,self.matrix_height,g1,g2,g3) # pure green
                        self.last_message = SharedState.shared_data["hash"]

                    time.sleep(self.update_interval)

                # Wait until there is a message that the phase has actually changed
                time_wait = time.monotonic()
                while SharedState.shared_data["current_phase"] == "green" and run_event.is_set():
                    # Continue to move bikes
                    draw_rectangle_shade(0,self.matrix_height,g1,g2,g3) # Just to reset each bike frame 
                    move_bikes_green()
                    self.time_elapsed_bike = time.monotonic() - self.start_time_bike

                    time.sleep(self.update_interval)
                    if time.monotonic() >= time_wait + 60: # 60 sec w/o expected phase change
                        print("Green phase prediction time ended 60s ago, however no red phase message was received. Leaving green state...",flush=True)
                        SharedState.shared_data["current_phase"] = "awaiting_message"
                        break

            ## Red phase ##  
            elif SharedState.shared_data["current_phase"] == "red" or SharedState.shared_data["current_phase"] == "yellow":

                initialize_phase_variables()
                just_switched = True

                # Red phase while bike moving. The bike moves beyond the green phase until it is in centered position.
                self.last_bike_time = 0.0
                draw_rectangle(self.bike_box_height,self.matrix_height,r1,r2,r3) # Red               
                
                while((self.current_row < self.matrix_height) and run_event.is_set()):
                    self.time_elapsed_bike = time.monotonic() - self.start_time_bike
                    self.last_update_elapsed_sec = time.monotonic() - self.last_update_elapsed_time_start
                    
                    update_current_row()

                    if self.bike_still_moving:
                        draw_black_trend_rectangle(0,self.current_row,r1,r2,r3) # Black fade
                        move_bike_red()
                    else:
                        if just_switched:
                            draw_rectangle_shade(0,self.bike_box_height,r1,r2,r3) # Reset bottom bike box to shaded red
                            draw_bike(graphics.Color(self.max_white, self.max_white, self.max_white),self.bike_height,self.bike_center)
                            just_switched = False
                        draw_black_trend_rectangle(self.bike_box_height,self.current_row,r1,r2,r3) # Black fade

                    if SharedState.shared_data["hash"] != self.last_message: # This avoids updates with every message that would break animation. Problematic with additional info in shared data.
                        if SharedState.shared_data["current_phase"] != "red" and SharedState.shared_data["current_phase"] !="yellow":
                            break
                        process_prediction_update()
                        draw_rectangle(self.bike_box_height+self.current_row,self.matrix_height,r1,r2,r3) # pure red 
                        self.last_message = SharedState.shared_data["hash"] 

                    time.sleep(self.update_interval)

                # Wait until there is a message that the phase has actually changed
                time_wait = time.monotonic()
                while SharedState.shared_data["current_phase"] == "red" and run_event.is_set():
                    time.sleep(0.1)
                    if time.monotonic() >= time_wait + 60: # 60 sec w/o expected phase change
                        print("Red phase prediction time ended 10s ago, however no green phase message was received. Leaving red state...",flush=True)
                        SharedState.shared_data["current_phase"] = "awaiting_message"
                        break

            elif SharedState.shared_data["current_phase"] == "awaiting_message":
                time_wait = time.monotonic()
                print("Awaiting message...",flush=True)
                pulse = 255
                down = True
                while SharedState.shared_data["current_phase"] == "awaiting_message" and run_event.is_set():
                    time.sleep(0.1)
                    draw_bike(graphics.Color(pulse, pulse, pulse),self.bike_height,self.bike_center)
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
                        draw_rectangle(0,self.matrix_height,0,0,0)
                        self.matrix.SetPixel(1, 1, 10, 10, 10) # Debug pixel
                        while SharedState.shared_data["current_phase"] == "awaiting_message" and run_event.is_set():                                                      
                            time.sleep(1)
            else:
                print("Unknown phase / error: ",SharedState.shared_data,flush=True)
                draw_bike(graphics.Color(255,49,73),self.bike_height,self.bike_center)
                time.sleep(15)
                print("Trying again...",flush=True)
    
