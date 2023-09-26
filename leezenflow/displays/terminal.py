import time
import copy

from leezenflow.displays import display
import leezenflow.shared_state as shared_state
from leezenflow.phase import TrafficLightPhase
from datetime import timedelta


class Terminal(display.AbstractLeezenflowDisplay):
    matrix_height = 96

    # terminal output variables
    firstRun = True
    firstLoop = True

    def __init__(self):
        # initialize array to hold r,g,b values for each pixel
        self.terminalPixelRow = [
            [[0, 0, 0] for j in range(self.COLS)] for i in range(self.ROWS)
        ]

        self.previousTerminalPixelRow = copy.deepcopy(self.terminalPixelRow)

    def update_frame(self):
        self.generate_table()

    def set_pixel(self, row, pixel, r, g, b):
        self.__setTerminalMatrixPixel(row, pixel, r, g, b)

    def generate_table(self):
        if self.firstLoop:
            time.sleep(1)
            self.firstLoop = False
        if shared_state.global_traffic_light_data is not None:
            current_phase = shared_state.global_traffic_light_data.movement_events[
                0
            ].current_phase
        else:
            current_phase = TrafficLightPhase.RED

        if not self.firstRun:
            pass
        else:
            for _ in self.terminalPixelRow:
                for i in _:
                    print("\033[0;30m● \033[0;0m", end="")  # print a colored point
                print()
            print()
            print()
            print(f"current_phase + {current_phase}")
            self.firstRun = False

        for i in range(len(self.terminalPixelRow)):
            for y in range(len(self.terminalPixelRow[i])):
                if (
                    self.terminalPixelRow[i][y][0]
                    != self.previousTerminalPixelRow[i][y][0]
                    or self.terminalPixelRow[i][y][1]
                    != self.previousTerminalPixelRow[i][y][1]
                    or self.terminalPixelRow[i][y][2]
                    != self.previousTerminalPixelRow[i][y][2]
                ):
                    print("\033[s", end="", flush=True)  # store current cursor position
                    print(
                        f"\033[{i + 4}A",
                        end="\x1b[2K",
                        flush=True,
                    )  # move i + 4 rows up and go to start of the line

                    for x in range(len(self.terminalPixelRow[i])):
                        print(
                            f"\x1b[38;2;{self.terminalPixelRow[i][x][0]};{self.terminalPixelRow[i][x][1]};{self.terminalPixelRow[i][x][2]}m● \x1b[0m",  # noqa: E501
                            end="",
                            flush=True,
                        )
                    print("\033[u", end="", flush=True)  # restore cursor position
                    break

        if shared_state.global_traffic_light_data is not None:
            remainingTimeInPhase = (
                shared_state.global_traffic_light_data.movement_events[0].likely_time
            )
        else:
            remainingTimeInPhase = timedelta(seconds=0)

        print("\033[s", end="", flush=True)  # store current cursor position
        print(f"\033[{2}A", flush=True)  # go two rows up
        print(end="\x1b[2K", flush=True)  # go to beginning of the line

        print(
            f"Real Traffic Light: {current_phase} for {remainingTimeInPhase.total_seconds()}s",  # noqa: E501
            end="",
            flush=True,
        )

        print("\033[u", end="", flush=True)  # restore cursor position

        self.previousTerminalPixelRow = copy.deepcopy(self.terminalPixelRow)

    def __setTerminalMatrixPixel(self, row, pixel, r, g, b):
        r = self.__clamp(r, 0, 255)
        g = self.__clamp(g, 0, 255)
        b = self.__clamp(b, 0, 255)
        if row > 95 or pixel > 31 or pixel < 0 or row < 0:
            return
        row = self.__clamp(row, 0, 95)
        pixel = self.__clamp(pixel, 0, 31)

        self.terminalPixelRow[row][pixel][0] = round(r)
        self.terminalPixelRow[row][pixel][1] = round(g)
        self.terminalPixelRow[row][pixel][2] = round(b)

    def __clamp(self, n, minn, maxn):
        return max(min(maxn, n), minn)
