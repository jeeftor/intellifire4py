"""Test Local API Calls."""
from __future__ import annotations

import pytest

from intellifire4py.local_api import IntelliFireAPILocal
from aioresponses import aioresponses

IP = "192.168.1.1"
# Load good poll data (should be a fixutre)
BAD_JSON_TEXT = "abcd1234"


@pytest.mark.asyncio
async def test_poll(poll_response_text: str) -> None:
    """Test the api poll."""
    fireplace_ip = IP
    with aioresponses() as m:
        m.get(f"http://{fireplace_ip}/poll", status=404)
        m.get(f"http://{fireplace_ip}/poll", status=200, body=poll_response_text)
        m.get(f"http://{fireplace_ip}/poll", status=200, body=BAD_JSON_TEXT)

        # httpx_mock.add_response(url=f"http://{fireplace_ip}/poll", status_code=404)
        # httpx_mock.add_response(
        #     url=f"http://{fireplace_ip}/poll", status_code=200, text=poll_response_text
        # )
        # httpx_mock.add_response(
        #     url=f"http://{fireplace_ip}/poll", status_code=200, text=BAD_JSON_TEXT
        # )

        api = IntelliFireAPILocal(fireplace_ip=fireplace_ip)

        with pytest.raises(ConnectionError):
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

            await api.poll()


@pytest.mark.asyncio
async def test_control(user_id: str, api_key: str, challenge_text: str) -> None:
    """Test local control."""
    with aioresponses() as mocked:
        api = IntelliFireAPILocal(fireplace_ip=IP, user_id=user_id, api_key=api_key)

        mocked.get(f"http://{IP}/get_challenge", body=challenge_text)
        mocked.post(f"http://{IP}/post", status=200)
        await api.pilot_on()
        assert api.data.pilot_on is True
        mocked.get(f"http://{IP}/get_challenge", body=challenge_text)
        mocked.post(f"http://{IP}/post", status=200)
        await api.pilot_off()
        assert api.data.pilot_on is False
        mocked.get(f"http://{IP}/get_challenge", body=challenge_text)  # type: ignore[unreachable]
        mocked.post(f"http://{IP}/post", status=200)
        await api.flame_on()
        assert api.data.is_on is True
        mocked.get(f"http://{IP}/get_challenge", body=challenge_text)
        mocked.post(f"http://{IP}/post", status=200)

        await api.flame_off()
        assert api.data.is_on is False
        mocked.get(f"http://{IP}/get_challenge", body=challenge_text)
        mocked.post(f"http://{IP}/post", status=200)

        await api.set_sleep_timer(minutes=60)
        assert api.data.timeremaining_s == 60 * 60
        mocked.get(f"http://{IP}/get_challenge", body=challenge_text)
        mocked.post(f"http://{IP}/post", status=200)

        await api.set_sleep_timer(minutes=10)
        assert api.data.timeremaining_s == 60 * 10
        mocked.get(f"http://{IP}/get_challenge", body=challenge_text)
        mocked.post(f"http://{IP}/post", status=200)

        # #
        await api.set_lights(level=1)
        assert api.data.light_level == 1
        mocked.get(f"http://{IP}/get_challenge", body=challenge_text)
        mocked.post(f"http://{IP}/post", status=200)

        await api.set_flame_height(height=1)
        assert api.data.flameheight == 1
        mocked.get(f"http://{IP}/get_challenge", body=challenge_text)
        mocked.post(f"http://{IP}/post", status=200)

        await api.set_fan_speed(speed=1)
        assert api.data.fanspeed == 1


def test_needs_login() -> None:
    """Login test."""
    local_api = IntelliFireAPILocal(fireplace_ip="192.168.1.5")
    assert local_api._needs_login() is True
