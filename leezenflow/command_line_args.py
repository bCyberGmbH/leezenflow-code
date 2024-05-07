import argparse


class CommandLineArgs:
    _args = None

    @staticmethod
    def get_arguments():
        if CommandLineArgs._args is None:
            parser = argparse.ArgumentParser()

            levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
            parser.add_argument("--log-level", default="INFO", choices=levels)
            parser.add_argument("--log-file", default=False, type=bool)

            # RGB matrix arguments (Note default values)
            parser.add_argument(
                "-c",
                "--led-chain",
                action="store",
                help="Daisy-chained boards. Default: 1.",
                type=int,
            )
            parser.add_argument(
                "-P",
                "--led-parallel",
                action="store",
                help="For Plus-models or RPi2: parallel chains. 1..3. Default: 1",
                default=1,
                type=int,
            )
            parser.add_argument(
                "-p",
                "--led-pwm-bits",
                action="store",
                help="Bits used for PWM. Something between 1..11. Default: 11",
                default=11,
                type=int,
            )
            parser.add_argument(
                "-b",
                "--led-brightness",
                action="store",
                help="Sets brightness level. Default: 100. Range: 1..100",
                type=int,
            )
            parser.add_argument(
                "-m",
                "--led-gpio-mapping",
                help="Hardware Mapping: regular, adafruit-hat, adafruit-hat-pwm",
                choices=["regular", "adafruit-hat", "adafruit-hat-pwm"],
                default="adafruit-hat-pwm",
                type=str,
            )
            parser.add_argument(
                "--led-scan-mode",
                action="store",
                help="Progressive or interlaced scan. 0 Progressive, 1 Interlaced (default)",  # noqa: E501
                default=1,
                choices=range(2),
                type=int,
            )
            parser.add_argument(
                "--led-pwm-lsb-nanoseconds",
                action="store",
                help="Base time-unit for the on-time in the lowest significant bit in nanoseconds. Default: 130, our default 250",  # noqa: E501
                type=int,
            )
            parser.add_argument(
                "--led-show-refresh",
                action="store_true",
                help="Shows the current refresh rate of the LED panel",
            )
            parser.add_argument(
                "--led-slowdown-gpio",
                action="store",
                help="Slow down writing to GPIO. Range: 0..4. Default: 3",
                type=int,
            )  # 3 best while testing at Swarco; 2 for local mqtt test
            parser.add_argument(
                "--led-no-hardware-pulse",
                action="store",
                help="Don't use hardware pin-pulse generation",
            )
            parser.add_argument(
                "--led-rgb-sequence",
                action="store",
                help="Switch if your matrix has led colors swapped. Default: RGB",
                default="RGB",
                type=str,
            )
            parser.add_argument(
                "--led-pixel-mapper",
                action="store",
                help='Apply pixel mappers. e.g "Rotate:90"',
                default="Rotate:0",
                type=str,
            )
            parser.add_argument(
                "--led-row-addr-type",
                action="store",
                help="0 = default; 1=AB-addressed panels; 2=row direct; 3=ABC-addressed panels; 4 = ABC Shift + DE direct",  # noqa: E501
                default=0,
                type=int,
                choices=[0, 1, 2, 3, 4],
            )
            parser.add_argument(
                "--led-multiplexing",
                action="store",
                help="Multiplexing type: 0=direct; 1=strip; 2=checker; 3=spiral; 4=ZStripe; 5=ZnMirrorZStripe; 6=coreman; 7=Kaler2Scan; 8=ZStripeUneven... (Default: 0)",  # noqa: E501
                type=int,
            )
            parser.add_argument(
                "--led-panel-type",
                action="store",
                help="Needed to initialize special panels. Supported: 'FM6126A'",
                default="",
                type=str,
            )

            # Leezenflow arguments
            parser.add_argument(
                "--receiver",
                action="store",
                help="How messages should be received. 'mqtt' or 'simulation' (Default: mqtt)",  # noqa: E501
                default="mqtt",
                choices=["mqtt", "simulation"],
                type=str,
            )
            parser.add_argument(
                "--test",
                action="store",
                help="Use a test dataset (instead of using live data via a receiver). (Default: -1)",  # noqa: E501
                default=-1,
                type=int,
            )

            parser.add_argument(
                "--distance",
                action="store",
                help="Select a distance between the traffic light and the leezenflow in meters (Default: 0)",  # noqa: E501
                default=0,
                type=int,
            )
            parser.add_argument(
                "--bicycle-speed",
                action="store",
                help="Select the average speed from the cyclist between the traffic light and the leezenflow in km/h (Default: 0)",  # noqa: E501
                default=0,
                type=int,
            )
            parser.add_argument(
                "--bicycle-yellow-speed",
                action="store",
                help="Select the speed from the cyclist that is needed to reach the traffic light when the leezenflow shows yellow in km/h (Default: 0)",  # noqa: E501
                default=0,
                type=int,
            )
            parser.add_argument(
                "--display",
                help="Select the output device (Default: led_panel)",
                choices=["led_panel", "terminal", "none"],
                default="led_panel",
                type=str,
            )
            parser.add_argument(
                "--signal-group",
                action="store",
                help="Select the signal group of the traffic light.",
                default=-1,
                type=int,
            )

            parser.add_argument(
                "--lsa-id",
                action="store",
                help="Select the lsa id of the intersection.",
                default=-1,
                type=int,
            )

            parser.add_argument(
                "--simulation",
                action="store",
                help="Methodname of simulation to run. (Default: log_simulation)",
                default="log_simulation",
                choices=["log_simulation", "phase_switch_simulation"],
                type=str,
            )

            parser.add_argument(
                "--led-panel",
                action="store",
                help="Choose the type of led-panel that is used",
                default="indoor",
                choices=["indoor", "outdoor"],
                type=str,
            )

            command_line_args = parser.parse_args()
            CommandLineArgs._args = command_line_args
        return CommandLineArgs._args
