import time
import argparse

from leezenflow_base import LeezenflowBase
from rgbmatrix import graphics

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
    parser.add_argument("--receiver", action="store", help="How are messages received. 0=None, 1=MQTT, 2=UDP", default=0, type=int)
    parser.add_argument("--test", action="store", help="Use test dataset.", default=-1, type=int)
    parser.add_argument("--logging", action="store", help="1=Log all messages. Default:0 ", default=0, type=int)
    parser.add_argument("--stats", action="store", help="1=Store phase changes of month to csv. Default:0 ", default=0, type=int)
    parser.add_argument("--animation", action="store", help="Select animation: 0-1", default=0, type=int)
    parser.add_argument("--modifier", action="store", help="Select a modifier to smooth inaccurate predictions.", default=0, type=int)

    command_line_args = parser.parse_args()
    if command_line_args.animation == 0:    
        from animations.animation_original import AnimationOrignal
        lf = AnimationOrignal(command_line_args)
    elif command_line_args.animation == 1: 
        from animations.animation_mshack import AnimationMSHACK
        lf = AnimationMSHACK(command_line_args)
    elif command_line_args.animation == 2: 
        from animations.animation_bar import AnimationBar
        lf = AnimationBar(command_line_args)
    elif command_line_args.animation == 3: 
        from animations.animation_bar_counter import AnimationBarCounter
        lf = AnimationBarCounter(command_line_args)    
    elif command_line_args.animation == 4: 
        from animations.animation_bar_counter_transition import AnimationBarCounterTransition
        lf = AnimationBarCounterTransition(command_line_args)    
    elif command_line_args.animation == 5: 
        from animations.animation_signal import AnimationSignal
        lf = AnimationSignal(command_line_args)
    else:
        print("Please select a valid animation.")
        
    if (not lf.process()):
        lf.print_help()

