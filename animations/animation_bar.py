from leezenflow_base import LeezenflowBase
from rgbmatrix import graphics
import time

class AnimationBar(LeezenflowBase):
    def __init__(self, command_line_args):
        super(AnimationBar, self).__init__(command_line_args)

        self.COLOR_GREEN = (0,255,132)
        self.COLOR_RED = (255,49,73)
        self.LENGTH_SHADE = 25  # Number shaded pixels
        self.BIAS = 5 # Reduces starting position of row 
        self.STATIC_DECREASE_RATE = 1 # For short phases (yellow, red-yellow)
        self.BORDER = 1.0

        self.UPDATE_INTERVAL = 0.2 # In seconds, such that CPU does not calculate maximum updates
        self.UPDATE_INTERVAL_ANIMATION = 0.1 # In seconds
        self.MATRIX_HEIGHT = 96
        self.MATRIX_WIDTH = 32                

        self.current_row = 96.0
       
    def run(self,_,run_event):

        g1,g2,g3 = *self.COLOR_GREEN,
        r1,r2,r3 = *self.COLOR_RED,
        canvas = self.matrix

        # Function to manually draw a bike 
        def draw_bike(color,y_position,axis_x_left):
            axis_x_left = axis_x_left
            axis_y = y_position
            axis_x_middle = axis_x_left + 7
            axis_x_right = axis_x_left + 15
            radius = 5

            # Wheels
            graphics.DrawCircle(canvas, axis_y, axis_x_left, radius, color)
            graphics.DrawCircle(canvas, axis_y, axis_x_right, radius, color)

            graphics.DrawLine(canvas, axis_y, axis_x_left, axis_y, axis_x_middle, color)
            graphics.DrawLine(canvas, axis_y, axis_x_left, axis_y+8, axis_x_left+4, color)
            graphics.DrawLine(canvas, axis_y, axis_x_middle, axis_y+8,  axis_x_middle+4, color)
            graphics.DrawLine(canvas, axis_y+8, axis_x_left+4, axis_y+8,  axis_x_middle+4, color)
            graphics.DrawLine(canvas, axis_y, axis_x_right, axis_y+8, axis_x_right-4, color)
            graphics.DrawLine(canvas, axis_y+8,  axis_x_middle+4, axis_y+10,  axis_x_middle+5, color)
            graphics.DrawLine(canvas, axis_y+10,  axis_x_middle+5, axis_y+10,  axis_x_middle+7, color)
            graphics.DrawLine(canvas, axis_y+9, axis_x_left+4, axis_y+10,  axis_x_left+3, color)
            graphics.DrawLine(canvas, axis_y+11,  axis_x_left+1, axis_y+11,  axis_x_left+5, color)

        def draw_rectangle(x0,y0,x1,y1,r,g,b):
            for row in range(y0,y1):
                graphics.DrawLine(canvas, row, x0, row, x1, graphics.Color(r,g,b))

        def draw_boder_top_bottom(r,g,b):
            max = self.MATRIX_HEIGHT-1
            graphics.DrawLine(canvas, 0, 0, 0, self.MATRIX_WIDTH - 1, graphics.Color(r,g,b))
            graphics.DrawLine(canvas, max, 0, max, self.MATRIX_WIDTH - 1, graphics.Color(r,g,b))

        # y = position where the fade starts
        def draw_bar(y,r,g,b):
            y -= self.BIAS
            length = self.LENGTH_SHADE
            r1 = r/length
            g1 = g/length
            b1 = b/length

            border = int(self.BORDER)
            x1 = int(self.MATRIX_WIDTH - self.BORDER - 1)

            for row in range(0,length): # Fade; middle
                graphics.DrawLine(canvas, row+y, border, row+y, x1, graphics.Color(r1*(row+1), g1*(row+1), b1*(row+1)))
            draw_rectangle(x0=border,y0=border,x1=x1,y1=y,r=r1/2,g=g1/2,b=b1/2) # Dark red/green; bottom
            draw_boder_top_bottom(r,g,b)

        def get_decrease_rate():
            remaining_time = max(0.1, self.shared_data["change_timestamp"] - self.shared_data["current_timestamp"]) # Avoids divide by zero 
            return (self.MATRIX_HEIGHT - self.current_row) / remaining_time # E.g. 3 rows per s

        def draw_phase(phase_primary, phase_secondary, color1, color2, color3):
            canvas.Fill(color1,color2,color3)
            self.current_row = self.BORDER # E.g. 1.0
            timer = time.monotonic() # In seconds

            while((self.current_row < (self.MATRIX_HEIGHT)) and run_event.is_set()):
                if timer + self.UPDATE_INTERVAL_ANIMATION <= time.monotonic():
                    if self.shared_data["current_phase"] == phase_secondary:
                        decrease_rate = self.STATIC_DECREASE_RATE
                    else:
                        decrease_rate = get_decrease_rate()

                    self.current_row = min(self.MATRIX_HEIGHT - 1, self.current_row + (decrease_rate * (time.monotonic() - timer)))
                    #print(decrease_rate, self.current_row)
                    draw_bar(int(self.current_row),color1,color2,color3)
                    timer = time.monotonic()

                if self.shared_data["current_phase"] != phase_primary and self.shared_data["current_phase"] != phase_secondary:
                    break

                time.sleep(self.UPDATE_INTERVAL)

        ### Start the loop ###
        while(run_event.is_set()):
        
            ## Green phase ##
            if self.shared_data["current_phase"] == "green" or self.shared_data["current_phase"] == "red-yellow":
                draw_phase("green","red-yellow",g1,g2,g3)
              
            ## Red phase ##
            elif self.shared_data["current_phase"] == "red" or self.shared_data["current_phase"] == "yellow":
                draw_phase("red","yellow",r1,r2,r3)

            ## Draws a pulsing bike while awaiting message  ##
            else:
                time_wait = time.monotonic()
                print("Awaiting message...",flush=True)
                pulse = 255
                down = True
                if self.shared_data["current_phase"] == "awaiting_message":
                    while self.shared_data["current_phase"] == "awaiting_message" and run_event.is_set():
                        time.sleep(0.1)
                        draw_bike(graphics.Color(pulse, pulse, pulse),8,8)
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
                        if time.monotonic() >= time_wait + 600: # After 10 min exit pulsing bike and show a single pixel
                            canvas.Fill(color1,color2,color3)
                            canvas.SetPixel(1, 1, 20, 20, 20) # Debug indicator pixel at position (1,1)
                            while self.shared_data["current_phase"] == "awaiting_message" and run_event.is_set():                                                      
                                time.sleep(1)
                else:
                    print("Unknown phase / error: ",self.shared_data,flush=True)
                    canvas.SetPixel(1, self.MATRIX_WIDTH - 2, 255, 49, 73) # Red error indicator pixel
                    time.sleep(2)
                    print("Trying again...",flush=True)
