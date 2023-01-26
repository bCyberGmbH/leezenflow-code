import time
import threading
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from displays import display

class Terminal(display.AbstractLeezenflowDisplay):
    cols = 32
    rows = 96
    values = 3

    length_shade = 25
    bias = 3

    def __init__(self):
        self.terminalPixelRow = [[[0 for k in range(self.values)] for j in range(self.cols)] for i in range(self.rows)]
        t3 = testThread(1 , "a", self.terminalPixelRow)
        t3.start()

    def GetDisplayType(self):
        print("Display: Terminal")

    def setPixel(self, row, pixel, r, g, b):
        self.__setTestMatrixPixel(row, pixel, r, g, b)

    def Fill(self, r, g, b):
        for row in range(0, self.rows):
            for pixel in range(0, self.cols):
                self.setPixel(row, pixel, r, g, b)

    def setRow(self, row_nr):
        for pixel in range(0, self.cols):
            self.setPixel(row_nr, pixel, 0, 0, 0)

    def draw_rectangle(self, y1, y2, r, g, b):
        for row in range(y1,y2):
            for pixel in range(0, self.cols):
                self.setPixel(row, pixel, r, g, b)

    def draw_rectangle_shade(self, y1, y2, r, g, b):
        shade_intensity = self.length_shade *2
        for row in range(y1,y2):
            for pixel in range(0, self.cols):
                self.setPixel(row, pixel, r/shade_intensity, g/shade_intensity, b/shade_intensity)

    def draw_black_trend_rectangle(self, y1, y2, r, g, b):
        y1 -= self.bias
        y2 -= self.bias
        length = self.length_shade # How many shaded pixel?
        r1 = r/length
        g1 = g/length
        b1 = b/length

        for row in range(0,length): # Fade of length 25 upwards starting at y2
            for pixel in range(0, self.cols):
                self.setPixel(y2+row, pixel, r1*(row+1), g1*(row+1), b1*(row+1))

        for row in range(y1,y2): # Plain dark green/red at the bottom
            for pixel in range(0,self.cols):
                self.setPixel(row, pixel, r1/2, g1/2, b1/2)

    def draw_bike(self, r, g, b, y_position, axis_x_left, moving = False):
        axis_x_left = axis_x_left
        axis_y = y_position
        axis_x_middle = axis_x_left + 7
        axis_x_right = axis_x_left + 15
        radius = 5
        self.__DrawCircle(axis_y, axis_x_left, radius, 255, 255, 255) # testMatrix
        self.__DrawCircle(axis_y, axis_x_right, radius, 255, 255, 255) # testMatrix

        if moving:
            # Speed lines
            self.__DrawLine(axis_y-radius+1, axis_x_left-radius-7, axis_y-radius+1, axis_x_left-radius-1, 255, 255, 255)
            self.__DrawLine(axis_y-radius+4, axis_x_left-radius-4, axis_y-radius+4, axis_x_left-radius-2, 255, 255, 255)
            self.__DrawLine(axis_y-radius+8, axis_x_left-radius-6, axis_y-radius+8, axis_x_left-radius-2, 255, 255, 255)

        self.__DrawLine(axis_y, axis_x_left, axis_y, axis_x_middle, 255, 255, 255)
        self.__DrawLine(axis_y, axis_x_left, axis_y+8, axis_x_left+4, 255, 255, 255)
        self.__DrawLine(axis_y, axis_x_middle, axis_y+8,  axis_x_middle+4, 255, 255, 255)
        self.__DrawLine(axis_y+8, axis_x_left+4, axis_y+8,  axis_x_middle+4, 255, 255, 255)
        self.__DrawLine(axis_y, axis_x_right, axis_y+8, axis_x_right-4, 255, 255, 255)
        self.__DrawLine(axis_y+8,  axis_x_middle+4, axis_y+10,  axis_x_middle+5, 255, 255, 255)
        self.__DrawLine(axis_y+10,  axis_x_middle+5, axis_y+10,  axis_x_middle+7, 255, 255, 255)
        self.__DrawLine(axis_y+9, axis_x_left+4, axis_y+10,  axis_x_left+3, 255, 255, 255)
        self.__DrawLine(axis_y+11,  axis_x_left+1, axis_y+11,  axis_x_left+5, 255, 255, 255)



    # private

    def __DrawCircle(self, x0, y0, radius, r, g, b):
        x = radius
        y = 0
        radiusError = 1 - x

        while (y <= x):
            self.setPixel(x + x0, y + y0, r, g, b)
            self.setPixel(y + x0, x + y0, r, g, b)
            self.setPixel(-x + x0, y + y0, r, g, b)
            self.setPixel(-y + x0, x + y0, r, g, b)
            self.setPixel(-x + x0, -y + y0, r, g, b)
            self.setPixel(-y + x0, -x + y0, r, g, b)
            self.setPixel(x + x0, -y + y0, r, g, b)
            self.setPixel(y + x0, -x + y0, r, g, b)
            y += 1
            if (radiusError<0):
                radiusError += 2 * y + 1
            else:
                x -= 1
                radiusError+= 2 * (y - x + 1)

    def __DrawLine(self, x0, y0, x1, y1, r, g, b):
        dy = y1 - y0
        dx = x1 - x0
        gradient = 0
        x = 0
        y = 0
        shift = 0x10

        if abs(dx) > abs(dy):
            # x variation is bigger than y variation
            if x1 < x0:
                x0, x1 = x1, x0
                y0, y1 = y1, y0
            gradient = (dy << shift) / dx
            y = round(0x8000 + (y0 << shift))
            for x in range(x0, x1 + 1):
                self.setPixel(round(x), round(y) >> shift, r, g, b)
                y += gradient
        elif dy != 0:
            # y variation is bigger than x variation
            if y1 < y0:
                x0, x1 = x1, x0
                y0, y1 = y1, y0
            gradient = (dx << shift) / dy
            x = round(0x8000 + (x0 << shift))
            for y in range(y0, y1 + 1):
                self.setPixel(round(x) >> shift,  round(y), r, g, b)
                x += gradient
        else:
            self.setPixel(round(x0), round(y0), r, g, b)

    def __setTestMatrixPixel(self, row, pixel, r, g, b):
        r = self.__clamp(r, 0, 255)
        g = self.__clamp(g, 0, 255)
        b = self.__clamp(b, 0, 255)
        if row >  95 or pixel > 31 or pixel < 0 or row < 0:
            return
        row = self.__clamp(row, 0, 95)
        pixel = self.__clamp(pixel, 0, 31)

        self.terminalPixelRow[row][pixel][0] = round(r)
        self.terminalPixelRow[row][pixel][1] = round(g)
        self.terminalPixelRow[row][pixel][2] = round(b)

    
    def __clamp(self, n, minn, maxn):
        return max(min(maxn, n), minn)


class testThread(threading.Thread):
    def __init__(self, iD, name, terminalPixelRow):
        threading.Thread.__init__(self)
        self.iD = iD
        self.name = name
        self.firstRun = True
        self.firstLoop = True
        self.cols = 32
        self.rows = 96
        self.values = 3
        self.previousTerminalPixelRow = [[[0 for k in range(self.values)] for j in range(self.cols)] for i in range(self.rows)]
        self.terminalPixelRow = terminalPixelRow

    def run(self):
        
        def generate_table():
            current_phase = display.AbstractLeezenflowDisplay.SharedState.shared_data["current_phase"]

            if not self.firstRun:
                pass
            else:
                for _ in self.terminalPixelRow:
                    for i in _:
                        print ("\033[0;31m● \033[0;0m",end="") # print a colored point
                    print()
                print()
                print()
                print(f"current_phase + {current_phase}")
                self.firstRun = False

            for i in range(len(self.terminalPixelRow)):
                for y in range(len(self.terminalPixelRow[i])):
                    if (self.terminalPixelRow[i][y][0] != self.previousTerminalPixelRow[i][y][0] or self.terminalPixelRow[i][y][1] != self.previousTerminalPixelRow[i][y][1] or self.terminalPixelRow[i][y][2] != self.previousTerminalPixelRow[i][y][2]):
                        print('\033[s', end='', flush=True) # store current cursor position
                        print(f'\033[{i + 4}A', end='\x1b[2K', flush=True) # move i + 4 rows up and go to start of the line

                        for x in range(len(self.terminalPixelRow[i])):
                            print(f"\x1b[38;2;{self.terminalPixelRow[i][x][0]};{self.terminalPixelRow[i][x][1]};{self.terminalPixelRow[i][x][2]}m● \x1b[0m",end='', flush=True)
                        print('\033[u', end='', flush=True) # restore cursor position
                        break


            remainingTimeInPhase = max(0, (display.AbstractLeezenflowDisplay.SharedState.shared_data["change_timestamp"] - display.AbstractLeezenflowDisplay.SharedState.shared_data["current_timestamp"]))

            print('\033[s', end='', flush=True) # store current cursor position
            print(f'\033[{2}A', flush=True) # go two rows up
            print(end='\x1b[2K', flush=True) # go to beginning of the line


            print(f"Current Traffic Light: {current_phase} for {remainingTimeInPhase} seconds", end='', flush=True)
            print('\033[u', end='', flush=True) # restore cursor position

            for row in range(0,self.rows):
                for pixel in range(0,32):
                    self.previousTerminalPixelRow[row][pixel][0] = self.terminalPixelRow[row][pixel][0]
                    self.previousTerminalPixelRow[row][pixel][1] = self.terminalPixelRow[row][pixel][1]
                    self.previousTerminalPixelRow[row][pixel][2] = self.terminalPixelRow[row][pixel][2]

        while True:
            if self.firstLoop:
                time.sleep(1)
                self.firstLoop = False
            generate_table()
            time.sleep(0.4)