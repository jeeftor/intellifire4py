"""Constants and Globals."""
import logging
from enum import Enum

from aenum import MultiValueEnum

_log = logging.getLogger(__package__)


class IntellifireErrorCode(MultiValueEnum):  # type: ignore
    """Error Class based on decompiled android apk code.

    private final Map<Integer, Integer> f6061f = c0.e(o.a(2, Integer.valueOf((int) C0189R.string.title_error_appliance_pilot_flame)), o.a(6, Integer.valueOf((int) C0189R.string.title_error_appliance_fan_delay)), o.a(4, Integer.valueOf((int) C0189R.string.title_error_appliance_flame)), o.a(64, Integer.valueOf((int) C0189R.string.title_error_appliance_maintenance)), o.a(129, Integer.valueOf((int) C0189R.string.title_error_appliance_disabled)), o.a(130, Integer.valueOf((int) C0189R.string.title_error_appliance_pilot_flame)), o.a(132, Integer.valueOf((int) C0189R.string.title_error_appliance_fan)), o.a(133, Integer.valueOf((int) C0189R.string.title_error_appliance_lights)), o.a(134, Integer.valueOf((int) C0189R.string.title_error_appliance_accessory)), o.a(144, Integer.valueOf((int) C0189R.string.title_error_appliance_soft_lock_out)), o.a(145, Integer.valueOf((int) C0189R.string.title_error_appliance_disabled)), o.a(642, Integer.valueOf((int) C0189R.string.title_error_appliance_offline)), o.a(3269, Integer.valueOf((int) C0189R.string.title_error_appliance_ecm_offline)));
    """

    PILOT_FLAME = 2, 130
    FLAME = 4
    FAN_DELAY = 6
    MAINTENANCE = 64
    DISABLED = 129, 145
    FAN = 132
    LIGHTS = 133
    ACCESSORY = 134
    SOFT_LOCK_OUT = 144
    ECM_OFFLINE = 3269
    OFFLINE = 642

    def get_message(self) -> str:
        """Get a message associated with the enum."""
        if self.name == "PILOT_FLAME":
            return "Pilot Flame Error: Your appliance has been safely disabled. Please contact your dealer and report this issue."
        if self.name == "FAN_DELAY":
            return "Fan Information: Fan will turn on within 3 minutes. Your appliance has a built-in delay that prevents the fan from operating within the first 3 minutes of turning on the appliance. This allows the air to be heated prior to circulation."
        if self.name == "FLAME":
            return "Pilot Flame Error. Your appliance has been safely disabled. Please contact your dealer and report this issue."
        if self.name == "MAINTENANCE":
            return "Maintenance: Your appliance is due for a routine maintenance check. Please contact your dealer to ensure your appliance is operating at peak performance."
        if self.name == "DISABLED":
            return "Appliance Safely Disabled: Your appliance has been disabled. Please contact your dealer and report this issue."
        if self.name == "FAN":
            return "Fan Error. Your appliance has detected that an accessory is not functional. Please contact your dealer and report this issue."
        if self.name == "LIGHTS":
            return "Lights Error. Your appliance has detected that an accessory is not functional. Please contact your dealer and report this issue."
        if self.name == "ACCESSORY":
            return "Your appliance has detected that an AUX port or accessory is not functional. Please contact your dealer and report this issue."
        if self.name == "SOFT_LOCK_OUT":
            return "Sorry your appliance did not start. Try again by pressing Flame ON."
        if self.name == "OFFLINE":
            return "Your appliance is currently offline."
        if self.name == "ECM_OFFLINE":
            return "ECM is offline."
        return "Unknown Error."


class IntellifireCommand(Enum):
    """Various commands as defined by Intellifire API/WebClient."""

    POWER = {"cloud_command": "power", "local_command": "power", "min": 0, "max": 1}
    PILOT = {"cloud_command": "pilot", "local_command": "pilot", "min": 0, "max": 1}
    BEEP = {
        "cloud_command": "beep",
        "local_command": "beep",
        "min": 1,
        "max": 1,
    }  # This doesn't actulaly seem to do anything
    LIGHT = {"cloud_command": "light", "local_command": "light", "min": 0, "max": 3}
    FLAME_HEIGHT = {
        "cloud_command": "height",
        "local_command": "flame_height",
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
    SOFT_RESET = {  # This can be used to "soft reset the unit" -> probably dont ever need it.
        "cloud_command": "soft_reset",
        "local_command": "soft_reset",  # Unaware of the local command for this one here
        "min": 1,
        "max": 1,
    }
