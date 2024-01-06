"""Test Local API Calls."""
from __future__ import annotations

from json import JSONDecodeError

import aiohttp
import pytest

from intellifire4py import UnifiedFireplace
from intellifire4py.cloud_interface import IntelliFireCloudInterface
from intellifire4py.const import IntelliFireCommand
from intellifire4py.exceptions import InputRangError
from intellifire4py.local_api import IntelliFireAPILocal
from aioresponses import aioresponses

IP = "192.168.1.69"
# Load good poll data (should be a fixutre)
BAD_JSON_TEXT = "abcd1234"


@pytest.mark.asyncio
async def test_poll(local_poll_json: str) -> None:
    """Test the api poll."""
    fireplace_ip = IP
    with aioresponses() as m:
        m.get(f"http://{fireplace_ip}/poll", status=404)
        m.get(f"http://{fireplace_ip}/poll", status=200, body=BAD_JSON_TEXT)
        m.get(f"http://{fireplace_ip}/poll", status=200, body=local_poll_json)
        api = IntelliFireAPILocal(fireplace_ip=fireplace_ip)

        with pytest.raises(aiohttp.ClientResponseError):
            await api.poll()

            assert api.data.name == ""
            assert api.data.serial == "BD0E054B5D6DF7AFBC8F9B28C9011111"
            assert api.data.temperature_c == 17
            assert api.data.pilot_on is False
            assert api.data.light_level == 3
            assert api.data.flameheight == 4
            assert api.data.is_hot is False
            assert api.data.is_on is False
            assert api.data.thermostat_on is False
            assert api.data.raw_thermostat_setpoint == 0
            assert api.data.timer_on is False
            assert api.data.has_light == 1
        with pytest.raises(JSONDecodeError):
            await api.poll()

        await api.poll()


@pytest.mark.asyncio
async def test_local_control(mock_login_for_control_testing):  # type: ignore
    """Test local tonrol options."""
    username = "user"
    password = "pass"  # noqa: S105
    async with IntelliFireCloudInterface() as cloud_interface:
        await cloud_interface.login_with_credentials(
            username=username, password=password
        )
        user_data = cloud_interface.user_data
        fireplaces = await UnifiedFireplace.build_fireplaces_from_user_data(user_data)
        fp = fireplaces[0]

        assert fp.data.serial == "BD0E054B5D6DF7AFBC8F9B28C9011111"
        assert fp.data.brand == "unset"
        assert fp.data.battery == 0
        assert fp.data.connection_quality == 995871
        await fp.read_api.start_background_polling()

        assert fp.read_api.is_polling_in_background == True  # noqa: E712

        await fp.control_api.pilot_on()
        assert fp.data.pilot_on is True
        await fp.control_api.flame_on()
        assert fp.data.is_on is True
        await fp.control_api.flame_off()
        await fp.control_api.soft_reset()
        await fp.control_api.stop_sleep_timer()
        await fp.control_api.set_thermostat_c(10)
        await fp.control_api.set_thermostat_f(70)
        await fp.control_api.turn_on_thermostat()
        await fp.control_api.turn_off_thermostat()
        await fp.control_api.fan_off()
        await fp.control_api.beep()

        assert fp.data.is_on is False

        assert fp.read_api.is_polling_in_background is True
        assert fp.read_api.data.name == ""
        assert fp.read_api.data.fw_version == "0x01030000"
        assert fp.read_api.data.fw_ver_str == "1.3.0"
        assert fp.read_api.data.has_power_vent is False
        assert fp.data.has_fan is True
        assert fp.data.ipv4_address == "192.168.1.69"
        await fp.read_api.stop_background_polling()

        with pytest.raises(InputRangError):
            await fp.control_api.send_command(
                command=IntelliFireCommand.FAN_SPEED, value=8
            )


@pytest.mark.asyncio
async def test_control_direct(user_id: str, api_key: str, challenge_text: str) -> None:
    """Test local control."""
    with aioresponses() as mocked:
        api = IntelliFireAPILocal(fireplace_ip=IP, user_id=user_id, api_key=api_key)

        mocked.get(f"http://{IP}/get_challenge", body=challenge_text, repeat=True)
        mocked.post(f"http://{IP}/post", status=200, repeat=True)
        await api.pilot_on()
        assert api.data.pilot_on is True
        await api.pilot_off()
        assert api.data.pilot_on is False
        await api.flame_on()
        assert api.data.is_on is True

        await api.flame_off()
        assert api.data.is_on is False

        await api.set_sleep_timer(minutes=60)
        assert api.data.timeremaining_s == 60 * 60

        await api.set_sleep_timer(minutes=10)
        assert api.data.timeremaining_s == 60 * 10

        await api.set_lights(level=1)
        assert api.data.light_level == 1

        await api.set_flame_height(height=1)
        assert api.data.flameheight == 1

        await api.set_fan_speed(speed=1)
        assert api.data.fanspeed == 1


def test_needs_login() -> None:
    """Login test."""
    local_api = IntelliFireAPILocal(fireplace_ip="192.168.1.5")
    assert local_api._needs_login() is True
