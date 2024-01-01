"""Test Local API Calls."""
from __future__ import annotations

from json import JSONDecodeError

import aiohttp
import pytest

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
