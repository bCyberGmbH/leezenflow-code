import abc

from leezenflow.phase import DisplayPhase


class AbstractLeezenflowDisplay(abc.ABC):
    ROWS = 96
    COLS = 32
    SHADE_ROWS = 25
    BIAS = 3

    COLOR_GREEN = (0, 255, 132)
    COLOR_RED = (255, 49, 73)
    COLOR_YELLOW = (255, 255, 0)
    COLOR_WHITE = (255, 255, 255)

    @abc.abstractmethod
    def set_pixel(self, row, pixel, r, g, b):
        pass

    def fill(self, r, g, b):
        for row in range(0, self.ROWS):
            for pixel in range(0, self.COLS):
                self.set_pixel(row, pixel, r, g, b)

    def draw_leezenflow(
        self, current_percentage_of_filling, current_phase: DisplayPhase
    ):
        length = self.SHADE_ROWS
        r = 0
        r1 = 0
        g = 0
        g1 = 0
        b = 0
        b1 = 0

        wert = (
            round(((100 - current_percentage_of_filling) / 100) * (self.ROWS - 23) + 23)
            + length
        )

        background_height = max(1, wert - self.BIAS - self.SHADE_ROWS)

        if current_phase == DisplayPhase.GREEN:
            r, g, b = (*self.COLOR_GREEN,)
        elif current_phase == DisplayPhase.RED:
            r, g, b = (*self.COLOR_RED,)
        elif current_phase == DisplayPhase.YELLOW:
            r, g, b = (*self.COLOR_YELLOW,)

        r1 = round(r / length)
        g1 = round(g / length)
        b1 = round(b / length)

        # full color
        for row in range(wert - self.BIAS, self.ROWS):
            for pixel in range(0, 32):
                self.set_pixel(row, pixel, r, g, b)

        # background
        for row in range(0, background_height):  # Plain dark green/red at the bottom
            for pixel in range(0, 32):
                self.set_pixel(row, pixel, r1 / 2, g1 / 2, b1 / 2)  # Dark green/red

        # shade
        for row in range(0, length):  # Fade of length 25 upwards starting at y2
            for pixel in range(0, 32):
                self.set_pixel(
                    (wert + row) - (length + self.BIAS),
                    pixel,
                    r1 * (row + 1),
                    g1 * (row + 1),
                    b1 * (row + 1),
                )

    def _draw_line(self, x0, y0, x1, y1, r, g, b):
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
                self.set_pixel(round(x), round(y) >> shift, r, g, b)
                y += gradient
        elif dy != 0:
            # y variation is bigger than x variation
            if y1 < y0:
                x0, x1 = x1, x0
                y0, y1 = y1, y0
            gradient = (dx << shift) / dy
            x = round(0x8000 + (x0 << shift))
            for y in range(y0, y1 + 1):
                self.set_pixel(round(x) >> shift, round(y), r, g, b)
                x += gradient
        else:
            self.set_pixel(round(x0), round(y0), r, g, b)

    def _draw_circle(self, x0, y0, radius, r, g, b):
        x = radius
        y = 0
        radiusError = 1 - x

        while y <= x:
            self.set_pixel(x + x0, y + y0, r, g, b)
            self.set_pixel(y + x0, x + y0, r, g, b)
            self.set_pixel(-x + x0, y + y0, r, g, b)
            self.set_pixel(-y + x0, x + y0, r, g, b)
            self.set_pixel(-x + x0, -y + y0, r, g, b)
            self.set_pixel(-y + x0, -x + y0, r, g, b)
            self.set_pixel(x + x0, -y + y0, r, g, b)
            self.set_pixel(y + x0, -x + y0, r, g, b)
            y += 1
            if radiusError < 0:
                radiusError += 2 * y + 1
            else:
                x -= 1
                radiusError += 2 * (y - x + 1)

    def _draw_bike(self, r, g, b, y_position, axis_x_left, moving=False):
        axis_x_left = axis_x_left
        axis_y = y_position
        axis_x_middle = axis_x_left + 7
        axis_x_right = axis_x_left + 15
        radius = 5
        self._draw_circle(axis_y, axis_x_left, radius, *self.COLOR_WHITE)
        self._draw_circle(axis_y, axis_x_right, radius, *self.COLOR_WHITE)

        if moving:
            # Speed lines
            self._draw_line(
                axis_y - radius + 1,
                axis_x_left - radius - 7,
                axis_y - radius + 1,
                axis_x_left - radius - 1,
                *self.COLOR_WHITE
            )
            self._draw_line(
                axis_y - radius + 4,
                axis_x_left - radius - 4,
                axis_y - radius + 4,
                axis_x_left - radius - 2,
                *self.COLOR_WHITE
            )
            self._draw_line(
                axis_y - radius + 8,
                axis_x_left - radius - 6,
                axis_y - radius + 8,
                axis_x_left - radius - 2,
                *self.COLOR_WHITE
            )

        self._draw_line(axis_y, axis_x_left, axis_y, axis_x_middle, *self.COLOR_WHITE)
        self._draw_line(
            axis_y, axis_x_left, axis_y + 8, axis_x_left + 4, *self.COLOR_WHITE
        )
        self._draw_line(
            axis_y, axis_x_middle, axis_y + 8, axis_x_middle + 4, *self.COLOR_WHITE
        )
        self._draw_line(
            axis_y + 8,
            axis_x_left + 4,
            axis_y + 8,
            axis_x_middle + 4,
            *self.COLOR_WHITE
        )
        self._draw_line(
            axis_y, axis_x_right, axis_y + 8, axis_x_right - 4, *self.COLOR_WHITE
        )
        self._draw_line(
            axis_y + 8,
            axis_x_middle + 4,
            axis_y + 10,
            axis_x_middle + 5,
            *self.COLOR_WHITE
        )
        self._draw_line(
            axis_y + 10,
            axis_x_middle + 5,
            axis_y + 10,
            axis_x_middle + 7,
            *self.COLOR_WHITE
        )
        self._draw_line(
            axis_y + 9, axis_x_left + 4, axis_y + 10, axis_x_left + 3, *self.COLOR_WHITE
        )
        self._draw_line(
            axis_y + 11,
            axis_x_left + 1,
            axis_y + 11,
            axis_x_left + 5,
            *self.COLOR_WHITE
        )
