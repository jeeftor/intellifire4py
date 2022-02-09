"""Constants and Globals."""
import logging
from enum import Enum

_log = logging.getLogger(__package__)


class IntellifireCommand(Enum):
    """Various commands as defined by Intellifire API/WebClient."""

    POWER = {"cloud_command": "power", "local_command": "power", "min": 0, "max": 1}
    PILOT = {"cloud_command": "pilot", "local_command": "pilot", "min": 0, "max": 1}
    BEEP = {"cloud_command": "beep", "local_command": "beep", "min": 1, "max": 1}
    LIGHT = {"cloud_command": "light", "local_command": "light", "min": 0, "max": 3}
    FLAME_HEIGHT = {
        "cloud_command": "height",
        "local_command": "height",
        "min": 0,
        "max": 4,
    }
    FAN_SPEED = {
        "cloud_command": "fanspeed",
        "local_command": "fan_speed",  # Local command uses fan_speed, cloud uses fanspeed
        "min": 0,
        "max": 4,
    }
    THERMOSTAT_SETPOINT = {
        "cloud_command": "thermostat_setpoint",
        "local_command": "thermostat_setpoint",
        "min": 0,
        "max": 3700,
    }  # 0 = disable thermostat
    TIME_REMAINING = {
        "cloud_command": "time_remaining",
        "local_command": "time_remaining",
        "min": 0,
        "max": 10800,
    }  # multiples of 60 - 0 = disable
    SOFT_RESET = (
        {  # This can be used to "soft reset the unit" -> probably dont ever need it.
            "cloud_command": "soft_reset",
            "local_command": "soft_reset",
            "min": 1,
            "max": 1,
        }
    )
