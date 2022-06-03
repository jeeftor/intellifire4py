"""Intellifire Tester."""
from unittest.mock import AsyncMock

import pytest

from intellifire4py.intellifire import IntellifireAPILocal


@pytest.fixture()
def mock_send_command(mocker):  # type: ignore
    """Mock send command."""
    async_mock = AsyncMock()
    mocker.patch(
        "intellifire4py.intellifire.IntellifireAPILocal.send_command",
        side_effect=async_mock,
    )
    return async_mock


@pytest.fixture()
def mock_get_challenge(mocker):  # type: ignore
    """Mock get challenge."""
    async_mock = AsyncMock()
    mocker.patch(
        "intellifire4py.intellifire.IntellifireAPILocal._get_challenge",
        side_effect=async_mock,
    )
    return async_mock


@pytest.fixture()
def mock_background_poll(mocker):  # type: ignore
    """Mock poll."""
    async_mock = AsyncMock()
    mocker.patch(
        "intellifire4py.intellifire.IntellifireAPILocal.__background_poll",
        side_effect=async_mock,
    )
    return async_mock


@pytest.mark.asyncio
async def test_send_local(mock_send_command, mock_background_poll):  # type: ignore
    """Test local command sending."""
    api = IntellifireAPILocal(fireplace_ip="192.168.1.5")
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
    api = IntellifireAPILocal(fireplace_ip="192.168.1.5")
    assert api._needs_login() is True
