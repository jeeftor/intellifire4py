"""IntelliFire Control Logic."""
from __future__ import annotations


from .const import IntelliFireCommand, IntelliFireApiMode
from abc import ABC, abstractmethod

from .model import IntelliFirePollData


class IntelliFireController(ABC):
    """Abstract base class to allow for the control of a fireplace."""

    def __init__(self, control_mode: IntelliFireApiMode):
        """Initialize the controller knowing whether its local or cloud based."""
        self._control_mode = control_mode
        self._data = IntelliFirePollData()

    async def flame_on(self) -> None:
        """Turn on the flame."""
        await self.send_command(command=IntelliFireCommand.POWER, value=1)
        self._data.is_on = True

    async def flame_off(self) -> None:
        """Turn off the flame."""
        await self.send_command(command=IntelliFireCommand.POWER, value=0)
        self._data.is_on = False

    async def pilot_on(self) -> None:
        """Turn on the pilot light."""
        await self.send_command(command=IntelliFireCommand.PILOT, value=1)
        self._data.pilot_on = True

    async def pilot_off(self) -> None:
        """Turn off the pilot light."""
        await self.send_command(command=IntelliFireCommand.PILOT, value=0)
        self._data.pilot_on = False

    async def set_lights(self, level: int) -> None:
        """Modify light levels."""
        await self.send_command(command=IntelliFireCommand.LIGHT, value=level)
        self._data.light_level = level

    async def set_flame_height(self, height: int) -> None:
        """Set flame height.

        Args:
            height (int): Valid height `0`-`4` (in the future this will be 1-5)
        """
        await self.send_command(command=IntelliFireCommand.FLAME_HEIGHT, value=height)
        self._data.flameheight = height

    async def set_fan_speed(self, speed: int) -> None:
        """Set fan speed."""
        await self.send_command(command=IntelliFireCommand.FAN_SPEED, value=speed)
        self._data.fanspeed = speed

    async def fan_off(self) -> None:
        """Turn fan off."""
        await self.set_fan_speed(speed=0)

    async def turn_off_thermostat(self) -> None:
        """Turn off thermostat mode."""
        await self.send_command(command=IntelliFireCommand.THERMOSTAT_SETPOINT, value=0)
        self._data.raw_thermostat_setpoint = 0

    async def turn_on_thermostat(self) -> None:
        """Turn on thermostat mode."""
        await self.send_command(
            command=IntelliFireCommand.THERMOSTAT_SETPOINT,
            value=self._last_thermostat_setpoint,
        )
        self._data.raw_thermostat_setpoint = self._last_thermostat_setpoint * 100

    async def set_thermostat_f(self, temp_f: int) -> None:
        """Set thermostat value in fahrenheit.

        Example:

            .. code:: Python

                # Set to 70 and store the value internally
                await ift_control.set_thermostat_f(temp_f=70)
                # Turn off thermostat
                await ift_control.turn_off_thermostat()
                # Turn on thermostat - will remember the last temp (70)
                await ift_control.turn_on_thermostat()
        """

        temp_c = int((temp_f - 32) * 5 / 9)
        await self.set_thermostat_c(temp_c=(temp_c))

    async def set_thermostat_c(self, temp_c: int) -> None:
        """Set thermostat value in centigrade."""
        self._last_thermostat_setpoint = temp_c
        # Need to multiply actual c value by 100 to meet
        # api specs. Not sure why :)
        await self.send_command(
            command=IntelliFireCommand.THERMOSTAT_SETPOINT,
            value=temp_c * 100,
        )
        self._data.raw_thermostat_setpoint = temp_c * 100

    async def set_sleep_timer(self, minutes: int) -> None:
        """Set the sleep timer in minutes.

        Args:
            minutes (int): Valid range `0`-`180`
        """
        await self.send_command(
            command=IntelliFireCommand.TIME_REMAINING,
            value=minutes * 60,  # api requires seconds - but we will work in minutes
        )
        self._data.timeremaining_s = 60 * minutes

    async def stop_sleep_timer(self) -> None:
        """Stop the sleep timer."""
        await self.send_command(command=IntelliFireCommand.TIME_REMAINING, value=0)
        self._data.timer_on = False
        self._data.timeremaining_s = 0

    async def soft_reset(self) -> None:
        """Issue a soft reset command (Cloud Only)."""
        await self.send_command(command=IntelliFireCommand.SOFT_RESET, value=1)

    async def beep(self) -> None:
        """Issue a beep command (Cloud Only)."""
        await self.send_command(command=IntelliFireCommand.BEEP, value=1)

    @abstractmethod
    async def send_command(
        self,
        *,
        command: IntelliFireCommand,
        value: int,
    ) -> None:
        """Send command stub."""
        return
