import time
import argparse
import threading

from leezenflow_base import LeezenflowBase
from leezenflow_display import LeezenflowDisplay
from command_line_args import CommandLineArgs

def create_Display(command_line_args, display_type):

    CommandLineArgs.command_line_args = command_line_args

    leezenflowDisplay = LeezenflowDisplay()

    leezenflowDisplay.setOutput(display_type)

    display = leezenflowDisplay.display

    if command_line_args.animation == 0:
        from animations.animation_original import AnimationOriginal
        lf = AnimationOriginal(command_line_args, display)
        t = threading.Thread(target=lf.process)
        t.start()
    elif command_line_args.animation == 1:
        from animations.animation_original_yellow import AnimationOriginalYellow
        lf = AnimationOriginalYellow(command_line_args, display)
        t = threading.Thread(target=lf.process)
        t.start()
    elif command_line_args.animation == 6:
        from animations.animation_original import AnimationOriginal
        lf = AnimationOriginal(command_line_args, display)
        t = threading.Thread(target=lf.process)
        t.start()
    elif command_line_args.animation == 7:
        from animations.animation_original_yellow import AnimationOriginalYellow
        lf = AnimationOriginalYellow(command_line_args, display)
        t = threading.Thread(target=lf.process)
        t.start()
    else:
        print("Please select a valid animation.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # RGB matrix arguments (Note default values)
    parser.add_argument("-r", "--led-rows", action="store", help="Display rows. 16 for 16x32, 32 for 32x32. Default: 32", default=32, type=int)
    parser.add_argument("--led-cols", action="store", help="Panel columns. Typically 32 or 64. (Default: 32)", default=96, type=int)
    parser.add_argument("-c", "--led-chain", action="store", help="Daisy-chained boards. Default: 1.", default=1, type=int)
    parser.add_argument("-P", "--led-parallel", action="store", help="For Plus-models or RPi2: parallel chains. 1..3. Default: 1", default=1, type=int)
    parser.add_argument("-p", "--led-pwm-bits", action="store", help="Bits used for PWM. Something between 1..11. Default: 11", default=11, type=int)
    parser.add_argument("-b", "--led-brightness", action="store", help="Sets brightness level. Default: 100. Range: 1..100", default=100, type=int)
    parser.add_argument("-m", "--led-gpio-mapping", help="Hardware Mapping: regular, adafruit-hat, adafruit-hat-pwm" , choices=['regular', 'adafruit-hat', 'adafruit-hat-pwm'], default='adafruit-hat-pwm',type=str)
    parser.add_argument("--led-scan-mode", action="store", help="Progressive or interlaced scan. 0 Progressive, 1 Interlaced (default)", default=1, choices=range(2), type=int)
    parser.add_argument("--led-pwm-lsb-nanoseconds", action="store", help="Base time-unit for the on-time in the lowest significant bit in nanoseconds. Default: 130", default=130, type=int)
    parser.add_argument("--led-show-refresh", action="store_true", help="Shows the current refresh rate of the LED panel")
    parser.add_argument("--led-slowdown-gpio", action="store", help="Slow down writing to GPIO. Range: 0..4. Default: 1", default=3, type=int) #3 best while testing at Swarco; 2 for local mqtt test
    parser.add_argument("--led-no-hardware-pulse", action="store", help="Don't use hardware pin-pulse generation")
    parser.add_argument("--led-rgb-sequence", action="store", help="Switch if your matrix has led colors swapped. Default: RGB", default="RGB", type=str)
    parser.add_argument("--led-pixel-mapper", action="store", help="Apply pixel mappers. e.g \"Rotate:90\"", default="Rotate:0", type=str)
    parser.add_argument("--led-row-addr-type", action="store", help="0 = default; 1=AB-addressed panels; 2=row direct; 3=ABC-addressed panels; 4 = ABC Shift + DE direct", default=0, type=int, choices=[0,1,2,3,4])
    parser.add_argument("--led-multiplexing", action="store", help="Multiplexing type: 0=direct; 1=strip; 2=checker; 3=spiral; 4=ZStripe; 5=ZnMirrorZStripe; 6=coreman; 7=Kaler2Scan; 8=ZStripeUneven... (Default: 0)", default=0, type=int)
    parser.add_argument("--led-panel-type", action="store", help="Needed to initialize special panels. Supported: 'FM6126A'", default="", type=str)

    # Leezenflow arguments
    parser.add_argument("--receiver", action="store", help="How messages should be received. 0=None, 1=MQTT, 2=UDP", default=0, type=int)
    parser.add_argument("--test", action="store", help="Use a test dataset (instead of using live data via a receiver).", default=-1, type=int)
    parser.add_argument("--animation", action="store", help="Select animation: 0,1,2,3,...", default=0, type=int)
    parser.add_argument("--modifier", action="store", help="Select a modifier to smooth inaccurate predictions.", default=0, type=int)
    parser.add_argument("--distance", action="store", help="Select a distance between the traffic light and the leezenflow in meters", default=0, type=int)
    parser.add_argument("--bicycle-speed", action="store", help="Select the average speed from the cyclist between the traffic light and the leezenflow in km/h", default=0, type=int)
    parser.add_argument("--bicycle-yellow-speed", action="store", help="Select the speed from the cyclist that is needed to reach the traffic light when the leezenflow shows yellow in km/h", default=0, type=int)
    parser.add_argument("--display", action="append", help="Select the output. If not specified, 'led_panel' will be selected. Possible options: 'terminal' or 'led_panel'")

    command_line_args = parser.parse_args()

    if (command_line_args.display != None and len(command_line_args.display) >= 1):
        for x in range(len(command_line_args.display)):
            create_Display(command_line_args, command_line_args.display[x])
    else:
        create_Display(command_line_args, "led_panel")



