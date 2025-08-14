"""Test control module for intellifire4py."""

import pytest
from intellifire4py.const import IntelliFireApiMode, IntelliFireCommand
from intellifire4py.control import IntelliFireController


class DummyController(IntelliFireController):
    """Dummy controller for testing."""

    async def send_command(self, command, value):
        """Mock send_command implementation."""
        self._last_command = (command, value)


@pytest.mark.asyncio
async def test_controller_basic_methods():
    """Test basic controller methods."""
    c = DummyController(IntelliFireApiMode.LOCAL)
    await c.flame_on()
    assert c._last_command == (IntelliFireCommand.POWER, 1)
    await c.flame_off()
    assert c._last_command == (IntelliFireCommand.POWER, 0)
    await c.pilot_on()
    assert c._last_command == (IntelliFireCommand.PILOT, 1)
    await c.pilot_off()
    assert c._last_command == (IntelliFireCommand.PILOT, 0)
    await c.set_lights(3)
    assert c._last_command == (IntelliFireCommand.LIGHT, 3)
    await c.set_flame_height(2)
    assert c._last_command == (IntelliFireCommand.FLAME_HEIGHT, 2)
    await c.set_fan_speed(1)
    # FAN_SPEED is the correct name in IntelliFireCommand
    assert c._last_command[0].name == "FAN_SPEED"
    assert c._last_command[1] == 1
