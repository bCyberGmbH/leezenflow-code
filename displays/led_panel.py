import time
import threading
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from displays import display
#from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics # rgbMatrix

class LED_Panel(display.AbstractLeezenflowDisplay):
    cols = 32
    rows = 96
    values = 3

    length_shade = 25
    bias = 3

    def __init__(self):
        from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics # rgbMatrix

        self.graphics = graphics

        options = RGBMatrixOptions()
        if display.AbstractLeezenflowDisplay.CommandLineArgs.command_line_args.led_gpio_mapping != None:
            options.hardware_mapping = display.AbstractLeezenflowDisplay.CommandLineArgs.command_line_args.led_gpio_mapping
        options.rows = display.AbstractLeezenflowDisplay.CommandLineArgs.command_line_args.led_rows
        options.cols = display.AbstractLeezenflowDisplay.CommandLineArgs.command_line_args.led_cols
        options.chain_length = display.AbstractLeezenflowDisplay.CommandLineArgs.command_line_args.led_chain
        options.parallel = display.AbstractLeezenflowDisplay.CommandLineArgs.command_line_args.led_parallel
        options.row_address_type = display.AbstractLeezenflowDisplay.CommandLineArgs.command_line_args.led_row_addr_type
        options.multiplexing = display.AbstractLeezenflowDisplay.CommandLineArgs.command_line_args.led_multiplexing
        options.pwm_bits = display.AbstractLeezenflowDisplay.CommandLineArgs.command_line_args.led_pwm_bits
        options.brightness = display.AbstractLeezenflowDisplay.CommandLineArgs.command_line_args.led_brightness
        options.pwm_lsb_nanoseconds = display.AbstractLeezenflowDisplay.CommandLineArgs.command_line_args.led_pwm_lsb_nanoseconds
        options.led_rgb_sequence = display.AbstractLeezenflowDisplay.CommandLineArgs.command_line_args.led_rgb_sequence
        options.pixel_mapper_config = display.AbstractLeezenflowDisplay.CommandLineArgs.command_line_args.led_pixel_mapper
        options.panel_type = display.AbstractLeezenflowDisplay.CommandLineArgs.command_line_args.led_panel_type
        if display.AbstractLeezenflowDisplay.CommandLineArgs.command_line_args.led_show_refresh:
            options.show_refresh_rate = 1
        if display.AbstractLeezenflowDisplay.CommandLineArgs.command_line_args.led_slowdown_gpio != None:
            options.gpio_slowdown = display.AbstractLeezenflowDisplay.CommandLineArgs.command_line_args.led_slowdown_gpio
        if display.AbstractLeezenflowDisplay.CommandLineArgs.command_line_args.led_no_hardware_pulse:
            options.disable_hardware_pulsing = True
        self.matrix = RGBMatrix(options = options)
        pass

        self.canvas = self.matrix

    def GetDisplayType(self):
        print("Display: LED-Panel")

    def setPixel(self, row, pixel, r, g, b):
        self.matrix.SetPixel(row, pixel, r, g, b)

    def Fill(self, r, g, b):
        self.matrix.Fill(0,0,0)

    def setRow(self, row_nr):
        for pixel in range(0,32):
            self.setPixel(row_nr, pixel, 0, 0, 0)

    def draw_rectangle(self, y1, y2, r, g, b):
        for row in range(y1,y2):
            for pixel in range(0,32):
                self.setPixel(row, pixel, r, g, b)

    def draw_rectangle_shade(self, y1, y2, r, g, b):
        shade_intensity = self.length_shade *2
        for row in range(y1,y2):
            for pixel in range(0,32):
                self.setPixel(row, pixel, r/shade_intensity, g/shade_intensity, b/shade_intensity)

    def draw_black_trend_rectangle(self, y1, y2, r, g, b):
        y1 -= self.bias
        y2 -= self.bias
        length = self.length_shade # How many shaded pixel?
        r1 = r/length
        g1 = g/length
        b1 = b/length

        for row in range(0,length): # Fade of length 25 upwards starting at y2
            for pixel in range(0,32):
                self.setPixel(y2+row, pixel, r1*(row+1), g1*(row+1), b1*(row+1))

        for row in range(y1,y2): # Plain dark green/red at the bottom
            for pixel in range(0,32):
                self.setPixel(row, pixel, r1/2, g1/2, b1/2) # Dark green/red

    def draw_bike(self, r, g, b, y_position, axis_x_left, moving = False):

        color = self.graphics.Color(255, 255, 255)

        axis_x_left = axis_x_left
        axis_y = y_position
        axis_x_middle = axis_x_left + 7
        axis_x_right = axis_x_left + 15
        radius = 5
        self.graphics.DrawCircle(self.canvas, axis_y, axis_x_left, radius, color)
        self.graphics.DrawCircle(self.canvas, axis_y, axis_x_right, radius, color)

        if moving:
            # Speed lines
            self.graphics.DrawLine(self.canvas, axis_y-radius+1, axis_x_left-radius-7, axis_y-radius+1, axis_x_left-radius-1, color)
            self.graphics.DrawLine(self.canvas, axis_y-radius+4, axis_x_left-radius-4, axis_y-radius+4, axis_x_left-radius-2, color)
            self.graphics.DrawLine(self.canvas, axis_y-radius+8, axis_x_left-radius-6, axis_y-radius+8, axis_x_left-radius-2, color)

        self.graphics.DrawLine(self.canvas, axis_y, axis_x_left, axis_y, axis_x_middle, color)
        self.graphics.DrawLine(self.canvas, axis_y, axis_x_left, axis_y+8, axis_x_left+4, color)
        self.graphics.DrawLine(self.canvas, axis_y, axis_x_middle, axis_y+8,  axis_x_middle+4, color)
        self.graphics.DrawLine(self.canvas, axis_y+8, axis_x_left+4, axis_y+8,  axis_x_middle+4, color)
        self.graphics.DrawLine(self.canvas, axis_y, axis_x_right, axis_y+8, axis_x_right-4, color)
        self.graphics.DrawLine(self.canvas, axis_y+8,  axis_x_middle+4, axis_y+10,  axis_x_middle+5, color)
        self.graphics.DrawLine(self.canvas, axis_y+10,  axis_x_middle+5, axis_y+10,  axis_x_middle+7, color)
        self.graphics.DrawLine(self.canvas, axis_y+9, axis_x_left+4, axis_y+10,  axis_x_left+3, color)
        self.graphics.DrawLine(self.canvas, axis_y+11,  axis_x_left+1, axis_y+11,  axis_x_left+5, color)


    # private