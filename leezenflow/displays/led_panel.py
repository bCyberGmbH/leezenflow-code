from leezenflow.displays import display
from leezenflow.command_line_args import CommandLineArgs


class LED_Panel(display.AbstractLeezenflowDisplay):
    def __init__(self):
        # lazy import to allow terminal output usage without installing this dependency
        from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics  # rgbMatrix

        self.graphics = graphics
        cli_args = CommandLineArgs.get_arguments()
        panel_type = cli_args.led_panel

        led_chain = 1
        multiplexing = 0
        led_slowdown_gpio = 3
        pwm_lsb_nanoseconds = 250
        brightness = 80

        if cli_args.led_chain is not None:
            led_chain = cli_args.led_chain
        elif panel_type == "indoor":
            led_chain = 1
        else:
            led_chain = 3

        if cli_args.led_multiplexing is not None:
            multiplexing = cli_args.led_multiplexing
        elif panel_type == "indoor":
            multiplexing = 0
        else:
            multiplexing = 2

        if cli_args.led_slowdown_gpio is not None:
            led_slowdown_gpio = cli_args.led_slowdown_gpio
        elif panel_type == "indoor":
            led_slowdown_gpio = 3
        else:
            led_slowdown_gpio = 2

        if cli_args.led_pwm_lsb_nanoseconds is not None:
            pwm_lsb_nanoseconds = cli_args.led_pwm_lsb_nanoseconds
        elif panel_type == "indoor":
            pwm_lsb_nanoseconds = 300
        else:
            pwm_lsb_nanoseconds = 450

        if cli_args.led_brightness is not None:
            brightness = cli_args.led_brightness
        elif panel_type == "indoor":
            brightness = 80
        else:
            brightness = 90

        options = RGBMatrixOptions()
        if cli_args.led_gpio_mapping is not None:
            options.hardware_mapping = cli_args.led_gpio_mapping
        # TODO: check why this is rotated and document/fix accordingly
        options.rows = self.COLS
        options.cols = self.ROWS if panel_type == "indoor" else 32
        options.chain_length = led_chain
        options.parallel = cli_args.led_parallel
        options.row_address_type = cli_args.led_row_addr_type
        options.multiplexing = multiplexing
        options.pwm_bits = cli_args.led_pwm_bits
        options.brightness = brightness
        options.pwm_lsb_nanoseconds = pwm_lsb_nanoseconds
        options.led_rgb_sequence = cli_args.led_rgb_sequence
        options.pixel_mapper_config = cli_args.led_pixel_mapper
        options.panel_type = cli_args.led_panel_type
        if cli_args.led_show_refresh:
            options.show_refresh_rate = 1
        options.gpio_slowdown = led_slowdown_gpio
        if cli_args.led_no_hardware_pulse:
            options.disable_hardware_pulsing = True
        self.matrix = RGBMatrix(options=options)
        self.offset_canvas = self.matrix.CreateFrameCanvas()
        pass

        self.canvas = self.matrix

    def update_frame(self):
        self.offset_canvas = self.matrix.SwapOnVSync(self.offset_canvas)

    def set_pixel(self, row, pixel, r, g, b):
        self.offset_canvas.SetPixel(row, pixel, r, g, b)
