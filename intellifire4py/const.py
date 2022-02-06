"""Constants and Globals."""
import logging
from enum import Enum

_log = logging.getLogger(__package__)


class IntellifireCommand(Enum):
    """Various commands as defined by Intellifire API/WebClient."""

    POWER = {"value": "power", "min": 0, "max": 1}
    PILOT = {"value": "pilot", "min": 0, "max": 1}
    BEEP = {"value": "beep", "min": 1, "max": 1}
    LIGHT = {"value": "light", "min": 0, "max": 3}
    FLAME_HEIGHT = {"value": "height", "min": 0, "max": 4}
    FAN_SPEED = {"value": "fanspeed", "min": 0, "max": 4}
    THERMOSTAT_SETPOINT = {"value": "thermostat_setpoint", "min": 0, "max": 37}
    TIME_REMAINING = {
        "value": "time_remaining",
        "min": 0,
        "max": 10800,
    }  # multiples of 60
