from rgbmatrix import graphics
import time
import threading

from leezenflow_base import LeezenflowBase
from shared_state import SharedState

cols = 32
rows = 96
values = 3
testPixelRow = [[[0 for k in range(values)] for j in range(cols)] for i in range(rows)]
# previousTestPixelRow = [[[0 for k in range(values)] for j in range(cols)] for i in range(rows)]

class testThread(threading.Thread):
    def __init__(self, iD, name):
        threading.Thread.__init__(self)
        self.iD = iD
        self.name = name
        self.firstRun = True
        self.cols = 32
        self.rows = 96
        self.values = 3
        self.previousTestPixelRow = [[[0 for k in range(values)] for j in range(cols)] for i in range(rows)]

    def run(self):
        print("start test run")

        # LINE_UP = '\033[1A'
        # LINE_CLEAR = '\x1b[2K'


          

        def generate_table():
            # print table
            counter = 0

            current_phase = SharedState.shared_data["current_phase"]

            if not self.firstRun:
                a = 1 + 1
                # LINE_UP = f'\033[{96}A' # old version
                # LINE_CLEAR = '\033[J' # old version
                # print(LINE_UP, end=LINE_CLEAR) # old version
            else:
                for _ in testPixelRow:
                    for i in _:
                        print ("\033[0;31m●\033[0;0m",end="")
                    print()
                print()
                print()
                print(f"current_phase + {current_phase}")
                self.firstRun = False

            for i in range(len(testPixelRow)):
                for y in range(len(testPixelRow[i])):
                    if (testPixelRow[i][y][0] != self.previousTestPixelRow[i][y][0] or testPixelRow[i][y][1] != self.previousTestPixelRow[i][y][1] or testPixelRow[i][y][2] != self.previousTestPixelRow[i][y][2]):
                        print('\033[s', end='', flush=True) # store current cursor position
                        print(f'\033[{i + 4}A', end='\x1b[2K', flush=True) # move i + 4 rows up and go to start of the line

                        for x in range(len(testPixelRow[i])):
                            print(f"\x1b[38;2;{testPixelRow[i][x][0]};{testPixelRow[i][x][1]};{testPixelRow[i][x][2]}m●\x1b[0m",end='', flush=True)
                        print('\033[u', end='', flush=True) # restore cursor position
                        break
                #print()
                    #else:
                        #print(f"gleich ==== an stelle {[i]}{[y]}")
                # for _ in range(i - 1):
                #     print()

            # print("\n")
            # counter += 1

            remainingTimeInPhase = max(0, (SharedState.shared_data["change_timestamp"] - SharedState.shared_data["current_timestamp"]))

            print('\033[s', end='', flush=True)
            print(f'\033[{2}A', flush=True)
            print(end='\x1b[2K', flush=True)


            print(f"Current Traffic Light: {current_phase} for {remainingTimeInPhase} seconds", end='', flush=True)
            print('\033[u', end='', flush=True) # restore cursor position

            # for _ in reversed(testPixelRow): # old version
            #     for i in _: # old version
            #         #self.console.print("●", style=f"rgb({i[0]},{i[1]},{i[2]})",end="") # old version
            #         #print(f"{i[0]};{i[1]};{i[2]}") # old version
            #         #print(f"\x1b[38;2;{i[0]};{i[1]};{i[2]}mTRUECOLOR\x1b[0m\n") # old version
            #         #print("\x1b[38;2;0;255;132m●\x1b[0m",end="") # old version
            #         print(f"\x1b[38;2;{i[0]};{i[1]};{i[2]}m●\x1b[0m",end="") # old version
            #         #print ("\033[0;31m●\033[0;0m",end="") # old version
            #     print() # old version
            #     counter += 1 # old version



            # for i in range(counter): # old version
            #     print(LINE_UP, end=LINE_CLEAR) # old version
            # print("\n") # old version
            # print("\n") # old version
            # print("\n") # old version
            # print("\n") # old version

            for row in range(0,self.rows):
                for pixel in range(0,32):
                    self.previousTestPixelRow[row][pixel][0] = testPixelRow[row][pixel][0]
                    self.previousTestPixelRow[row][pixel][1] = testPixelRow[row][pixel][1]
                    self.previousTestPixelRow[row][pixel][2] = testPixelRow[row][pixel][2]

        while True:
            generate_table()
            time.sleep(0.4)

class AnimationManu(LeezenflowBase):
    def __init__(self, command_line_args):
        super(AnimationManu, self).__init__(command_line_args)

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
        # self.LINE_UP = '\033[1A'
        # self.LINE_CLEAR = '\x1b[2K'
        self.cols = 32
        self.rows = 96
        self.values = 3
        #self.testPixelRow = [[[0 for k in range(self.values)] for j in range(self.cols)] for i in range(self.rows)]
        self.starttime = time.time()

    def run(self,_,run_event):

        g1,g2,g3 = *self.color_green,
        r1,r2,r3 = *self.color_red,
        canvas = self.matrix

        def testMatrixToCSV():
            #generate_table()
            
            a = 1 + 1


            # # self.console.print("Hello", style="rgb(175,0,255)")
            # # print("asdasdasd")
            # #f = open("/home/pi/leezenflow-code/demofile2.txt", "w")
            # #f = open("/home/pi/leezenflow-code/matrix_data.txt", "w")
            # #f.write("var matrix_data = " + str(self.testPixelRow))
            # #f.close()

            # import csv
            
            # with open("/home/pi/leezenflow-code/array_3D.csv","w") as my_csv:
            #     newarray = csv.writer(my_csv,delimiter=';')
            #     newarray.writerows(self.testPixelRow)

            # f = open("/home/pi/leezenflow-code/trafficLight.json", "w")
            # f.write(str(SharedState.shared_data))
            # f.close()


            #print(self.testPixelRow)


            # aktuell ->

            # counter = 0

            # current_phase = SharedState.shared_data["current_phase"]

            # print(f"Current phase: {current_phase}")
            # counter += 1

            # # # print("\n")
            # # # counter += 1

            # for _ in reversed(self.testPixelRow):
            #     for i in _:
            #         #self.console.print("●", style=f"rgb({i[0]},{i[1]},{i[2]})",end="")
            #         #print(f"{i[0]};{i[1]};{i[2]}")
            #         #print(f"\x1b[38;2;{i[0]};{i[1]};{i[2]}mTRUECOLOR\x1b[0m\n")
            #         #print("\x1b[38;2;0;255;132m●\x1b[0m",end="")
            #         # print(f"\x1b[38;2;{i[0]};{i[1]};{i[2]}m●\x1b[0m",end="")
            #         print ("\033[0;31m●\033[0;0m",end="")
            #     print()
            #     counter += 1

            # <- aktuell



            # for _ in self.testPixelRow:
            #     for i in _:
            #         #print(str(i[0]) + " " + str(i[1]) + " " + str(i[2]))
            #         if (i[0] == 255 and i[1] == 49 and i[2] == 73):
            #             print ("\033[0;31m●\033[0;0m",end="")
            #         elif (i[0] == 0 and i[1] == 255 and i[2] == 132):
            #             print ("\033[0;32m●\033[0;0m",end="")
            #         else:
            #             print ("\033[0;30m●\033[0;0m",end="")
            #         #print ("⬤ ",end=" ")
            #         #for y in i:
            #             #print(y,end=" ")
            #     print()
            #     counter += 1


            # for _ in self.testPixelRow:
            #     for i in _:
            #         self.console.print("●", style=f"rgb({i[0]},{i[1]},{i[2]})",end="")
            #     print()
            #     counter += 1
                    
            #os.system('clear')

            # print("\n")
            # counter += 1
            # print("\n")
            # counter += 1
            # print("\n")
            # counter += 1
            # print("\n")
            # counter += 1
            # print("\n")
            # counter += 1


            # aktuell ->

            # LINE_UP = f'\033[{counter}A'
            # LINE_CLEAR = '\033[J'

            # print(LINE_UP, end=LINE_CLEAR)

            # <- aktuell

            #print(f"\033[{counter}A")
            #print(f"\033[J")
            # for i in range(counter):
            #     print(self.LINE_UP, end=self.LINE_CLEAR)



        def clamp(n, minn, maxn):
            return max(min(maxn, n), minn)

        def setTestMatrixPixel(row, pixel, r, g, b):
            r = clamp(r, 0, 255)
            g = clamp(g, 0, 255)
            b = clamp(b, 0, 255)
            row = clamp(row, 0, 95)
            pixel = clamp(pixel, 0, 31)

            testPixelRow[row][pixel][0] = round(r)
            testPixelRow[row][pixel][1] = round(g)
            testPixelRow[row][pixel][2] = round(b)

        def setRow(row_nr):
            for pixel in range(0,32):
                self.matrix.SetPixel(row_nr, pixel, 0, 0, 0)
                setTestMatrixPixel(row_nr, pixel, 0, 0, 0)

        def draw_rectangle(y1,y2,r,g,b):
            
            for row in range(y1,y2):
                for pixel in range(0,32):
                    self.matrix.SetPixel(row, pixel, r, g, b)
                    setTestMatrixPixel(row, pixel, r, g, b)
            
        def draw_rectangle_shade(y1,y2,r,g,b):
            shade_intensity = self.length_shade *2
            for row in range(y1,y2):
                for pixel in range(0,32):
                    self.matrix.SetPixel(row, pixel, r/shade_intensity, g/shade_intensity, b/shade_intensity)
                    setTestMatrixPixel(row, pixel, r/shade_intensity, g/shade_intensity, b/shade_intensity)

        def draw_black_trend_rectangle(y1,y2,r,g,b):
            y1 -= self.bias
            y2 -= self.bias
            length = self.length_shade # How many shaded pixel?
            r1 = r/length
            g1 = g/length
            b1 = b/length

            for row in range(0,length): # Fade of length 25 upwards starting at y2
                for pixel in range(0,32):
                    self.matrix.SetPixel(y2+row, pixel, r1*(row+1), g1*(row+1), b1*(row+1))
                    setTestMatrixPixel(y2+row, pixel, r1*(row+1), g1*(row+1), b1*(row+1))

            for row in range(y1,y2): # Plain dark green/red at the bottom
                for pixel in range(0,32):
                    self.matrix.SetPixel(row, pixel, r1/2, g1/2, b1/2) # Dark green/red
                    setTestMatrixPixel(row, pixel, r1/2, g1/2, b1/2)


        #def DrawCircle(Canvas *c, int x0, int y0, int radius, const Color &color) {
        def DrawCircleForTestMatrix(x0, y0, radius, r, g, b):
            x = radius
            y = 0
            radiusError = 1 - x

            while (y <= x):
                # c->SetPixel(x + x0, y + y0, color.r, color.g, color.b);
                setTestMatrixPixel(x + x0, y + y0, r, g, b)
                # c->SetPixel(y + x0, x + y0, color.r, color.g, color.b);
                setTestMatrixPixel(y + x0, x + y0, r, g, b)
                # c->SetPixel(-x + x0, y + y0, color.r, color.g, color.b);
                setTestMatrixPixel(-x + x0, y + y0, r, g, b)
                # c->SetPixel(-y + x0, x + y0, color.r, color.g, color.b);
                setTestMatrixPixel(-y + x0, x + y0, r, g, b)
                # c->SetPixel(-x + x0, -y + y0, color.r, color.g, color.b);
                setTestMatrixPixel(-x + x0, -y + y0, r, g, b)
                # c->SetPixel(-y + x0, -x + y0, color.r, color.g, color.b);
                setTestMatrixPixel(-y + x0, -x + y0, r, g, b)
                # c->SetPixel(x + x0, -y + y0, color.r, color.g, color.b);
                setTestMatrixPixel(x + x0, -y + y0, r, g, b)
                # c->SetPixel(y + x0, -x + y0, color.r, color.g, color.b);
                setTestMatrixPixel(y + x0, -x + y0, r, g, b)
                y += 1
                if (radiusError<0):
                    radiusError += 2 * y + 1
                else:
                    x -= 1
                    radiusError+= 2 * (y - x + 1)
                
            
        


        # Function to manually draw a bike. It should also be possible (regarding performance) to include a .png graphic instead.
        def draw_bike(color,y_position,axis_x_left,moving=False):
            axis_x_left = axis_x_left
            axis_y = y_position
            axis_x_middle = axis_x_left + 7
            axis_x_right = axis_x_left + 15
            radius = 5

            # Wheels
            graphics.DrawCircle(canvas, axis_y, axis_x_left, radius, color)
            DrawCircleForTestMatrix(axis_y, axis_x_left, radius, 255, 255, 255) # testMatrix

            graphics.DrawCircle(canvas, axis_y, axis_x_right, radius, color)
            DrawCircleForTestMatrix(axis_y, axis_x_right, radius, 255, 255, 255) # testMatrix

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
                #print("Prediction <= 0.1", flush=True)
                return self.matrix_height
            self.current_row = self.last_update_current_row + int(((self.matrix_height - self.last_update_current_row) / self.last_update_prediction_sec) * self.last_update_elapsed_sec)

        def process_prediction_update():
            self.last_update_current_row = self.current_row
            self.last_update_elapsed_sec = 0
            if SharedState.shared_data["current_phase"] == "yellow" or SharedState.shared_data["current_phase"] == "red-yellow":
                self.last_update_prediction_sec = self.placeholder_time_for_short_phases
            else:
                self.last_update_prediction_sec = max(0, (SharedState.shared_data["change_timestamp"] - SharedState.shared_data["current_timestamp"]) - 10 )
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

            self.last_update_prediction_sec = max(0, (SharedState.shared_data["change_timestamp"] - SharedState.shared_data["current_timestamp"]) - 10)
            self.last_message = None
            self.current_row = self.bike_box_height
            self.last_update_current_row = self.current_row

        ### Start the loop ###
        while(run_event.is_set()):
            if self.testThreadStarted == False:
                self.testThreadStarted = True
                t3 = testThread(1 , "a")
                t3.start()

            ## Green phase ##
            if SharedState.shared_data["current_phase"] == "green" or SharedState.shared_data["current_phase"] == "red-yellow":

                # There are two bikes such that the second bike can roll into the matrix before the other has left 
                self.last_bike_time = 0.0
                self.bike1_position = 8 
                self.bike2_position = -999
                self.bike_still_moving = True

                self.switchedPhase = False

                initialize_phase_variables()
                if self.firstRun == True:
                    self.firstRun = False
                    draw_rectangle(self.bike_box_height,self.matrix_height,g1,g2,g3) # pure green
                    # testMatrixToCSV()
    
                while(self.current_row < self.matrix_height) and run_event.is_set():

                    self.time_elapsed_bike = time.monotonic() - self.start_time_bike
                    self.last_update_elapsed_sec = time.monotonic() - self.last_update_elapsed_time_start

                    update_current_row()
                    draw_black_trend_rectangle(0,self.current_row,g1,g2,g3) # Black fade and resetting of bike box
                    move_bikes_green()
                    # testMatrixToCSV()

                    if SharedState.shared_data["hash"] != self.last_message: # This avoids updates with every message that would break animation. Problematic with additional info in shared data.    
                        if SharedState.shared_data["current_phase"] != "green" and SharedState.shared_data["current_phase"] != "red-yellow":
                            break
                        process_prediction_update()
                        draw_rectangle(self.bike_box_height+self.current_row,self.matrix_height,g1,g2,g3) # pure green
                        self.last_message = SharedState.shared_data["hash"]
                        # testMatrixToCSV()

                        if SharedState.shared_data["current_phase"] == "green":
                            self.lastGreenPhaseTime = max(0, SharedState.shared_data["change_timestamp"] - SharedState.shared_data["current_timestamp"])
                            if len(self.greenPhaseArray) >= self.greenPhasesToSave:
                                self.greenPhaseArray.pop(0)
                            self.greenPhaseArray.append(self.lastGreenPhaseTime)
                            self.averageGreenPhaseTime = 0
                            for x in self.greenPhaseArray:
                                self.averageGreenPhaseTime += x
                            self.averageGreenPhaseTime = self.averageGreenPhaseTime / len(self.greenPhaseArray)
                            # erst benutzen, wenn 5-7 einträge da sind damit es genauer ist?

                    time.sleep(self.update_interval)

                self.switchedPhase = True
                while SharedState.shared_data["current_phase"] == "green" and (self.current_row >= self.matrix_height) and run_event.is_set():
                    self.current_row = self.bike_box_height
                    draw_rectangle(self.bike_box_height,self.matrix_height,r1,r2,r3) # pure green
                    # testMatrixToCSV()

                    while SharedState.shared_data["current_phase"] == "green":
                        
                        self.time_elapsed_bike = time.monotonic() - self.start_time_bike
                        self.last_update_elapsed_sec = time.monotonic() - self.last_update_elapsed_time_start

                        draw_black_trend_rectangle(0,self.current_row,r1,r2,r3) # Black fade and resetting of bike box
                        move_bike_red()
                        # testMatrixToCSV()

                        time.sleep(self.update_interval)

                # Wait until there is a message that the phase has actually changed
                time_wait = time.monotonic()
                while SharedState.shared_data["current_phase"] == "green" and run_event.is_set():
                    # Continue to move bikes
                    draw_rectangle_shade(0,self.matrix_height,g1,g2,g3) # Just to reset each bike frame 
                    move_bikes_green()
                    # testMatrixToCSV()
                    self.time_elapsed_bike = time.monotonic() - self.start_time_bike

                    time.sleep(self.update_interval)
                    if time.monotonic() >= time_wait + 60: # 60 sec w/o expected phase change
                        #print("Green phase prediction time ended 60s ago, however no red phase message was received. Leaving green state...",flush=True)
                        self.matrix.Fill(0,0,0)
                        # testMatrixToCSV()
                        SharedState.shared_data["current_phase"] = "awaiting_message"
                        break

            ## Red phase ##  
            elif SharedState.shared_data["current_phase"] == "red" or SharedState.shared_data["current_phase"] == "yellow":

                initialize_phase_variables()
                just_switched = True

                self.switchedPhase = False

                # Red phase while bike moving. The bike moves beyond the green phase until it is in centered position.
                self.last_bike_time = 0.0

                if self.firstRun == True:
                    self.firstRun = False
                    draw_rectangle(self.bike_box_height,self.matrix_height,r1,r2,r3) # Red               
                    # testMatrixToCSV()
                    
                while((self.current_row < self.matrix_height) and run_event.is_set()):
                    self.time_elapsed_bike = time.monotonic() - self.start_time_bike
                    self.last_update_elapsed_sec = time.monotonic() - self.last_update_elapsed_time_start
                    
                    update_current_row()

                    if self.bike_still_moving:
                        draw_black_trend_rectangle(0,self.current_row,r1,r2,r3) # Black fade
                        move_bike_red()
                        # testMatrixToCSV()
                    else:
                        if just_switched:
                            draw_rectangle_shade(0,self.bike_box_height,r1,r2,r3) # Reset bottom bike box to shaded red
                            draw_bike(graphics.Color(self.max_white, self.max_white, self.max_white),self.bike_height,self.bike_center)
                            just_switched = False
                            # testMatrixToCSV()
                        draw_black_trend_rectangle(self.bike_box_height,self.current_row,r1,r2,r3) # Black fade
                        # testMatrixToCSV()

                    if SharedState.shared_data["hash"] != self.last_message: # This avoids updates with every message that would break animation. Problematic with additional info in shared data.
                        if SharedState.shared_data["current_phase"] != "red" and SharedState.shared_data["current_phase"] !="yellow":
                            break
                        process_prediction_update()
                        draw_rectangle(self.bike_box_height+self.current_row,self.matrix_height,r1,r2,r3) # pure red
                        # testMatrixToCSV()
                        self.last_message = SharedState.shared_data["hash"]

                        if SharedState.shared_data["current_phase"] == "red":
                            self.lastRedPhaseTime = max(0, SharedState.shared_data["change_timestamp"] - SharedState.shared_data["current_timestamp"])
                            if len(self.redPhaseArray) >= self.redPhasesToSave:
                                self.redPhaseArray.pop(0)
                            self.redPhaseArray.append(self.lastRedPhaseTime)
                            self.averageRedPhaseTime = 0
                            for x in self.redPhaseArray:
                                self.averageRedPhaseTime += x
                            self.averageRedPhaseTime = self.averageRedPhaseTime / len(self.redPhaseArray)
                            # erst benutzen, wenn 5-7 einträge da sind?

                    time.sleep(self.update_interval)

                self.switchedPhase = True
                while SharedState.shared_data["current_phase"] == "red" and (self.current_row >= self.matrix_height) and run_event.is_set():
                    self.current_row = self.bike_box_height
                    draw_rectangle(self.bike_box_height,self.matrix_height,g1,g2,g3) # pure green
                    # testMatrixToCSV()

                    while SharedState.shared_data["current_phase"] == "red":
                        
                        self.time_elapsed_bike = time.monotonic() - self.start_time_bike
                        self.last_update_elapsed_sec = time.monotonic() - self.last_update_elapsed_time_start

                        #update_current_row()
                        draw_black_trend_rectangle(0,self.current_row,g1,g2,g3) # Black fade and resetting of bike box
                        move_bikes_green()
                        # testMatrixToCSV()

                        time.sleep(self.update_interval)



                # Wait until there is a message that the phase has actually changed
                time_wait = time.monotonic()
                while SharedState.shared_data["current_phase"] == "red" and run_event.is_set():
                    time.sleep(0.1)
                    if time.monotonic() >= time_wait + 60: # 60 sec w/o expected phase change
                        #print("Red phase prediction time ended 10s ago, however no green phase message was received. Leaving red state...",flush=True)
                        self.matrix.Fill(0,0,0)
                        # testMatrixToCSV()
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
    
