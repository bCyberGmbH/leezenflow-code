from enum import Enum


class TrafficLightPhase(Enum):
    """Possible traffic light phases."""

    RED = 1
    RED_YELLOW = 2
    GREEN = 3
    YELLOW = 4


class DisplayPhase(Enum):
    """Possible display/leezenflow light phases."""

    RED = 1
    GREEN = 2
    YELLOW = 3
