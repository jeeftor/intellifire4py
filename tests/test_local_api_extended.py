"""Extended tests for local_api.py to improve coverage."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from aioresponses import aioresponses
import aiohttp

from intellifire4py.local_api import IntelliFireAPILocal


@pytest.fixture
def local_api():
    """Create a local API instance for testing."""
    return IntelliFireAPILocal(
        fireplace_ip="192.168.1.100",
        user_id="test_user",
        api_key="deadbeefdeadbeefdeadbeefdeadbeef",
    )


@pytest.mark.asyncio
async def test_background_poll_timeout_handling(local_api):
    """Test background polling handles TimeoutError."""
    with aioresponses() as m:
        m.get(
            "http://192.168.1.100/poll",
            exception=asyncio.TimeoutError(),
            repeat=True,
        )

        await local_api.start_background_polling(minimum_wait_in_seconds=1)

        await asyncio.sleep(0.5)

        assert local_api.failed_poll_attempts > 0

        await local_api.stop_background_polling()


@pytest.mark.asyncio
async def test_poll_suppress_warnings_true(local_api):
    """Test poll with suppress_warnings=True."""
    with aioresponses() as m:
        m.get(
            "http://192.168.1.100/poll",
            status=404,
        )

        with pytest.raises(aiohttp.ClientResponseError):
            await local_api.poll(suppress_warnings=True)


@pytest.mark.asyncio
async def test_poll_timeout_suppress_warnings(local_api):
    """Test poll timeout with suppress_warnings=True."""
    with aioresponses() as m:
        m.get(
            "http://192.168.1.100/poll",
            exception=asyncio.TimeoutError(),
        )

        with pytest.raises(asyncio.TimeoutError):
            await local_api.poll(suppress_warnings=True, timeout_seconds=1)


@pytest.mark.asyncio
async def test_send_command_needs_login():
    """Test send_command when login is needed."""
    api = IntelliFireAPILocal(fireplace_ip="192.168.1.100")

    from intellifire4py.const import IntelliFireCommand

    with aioresponses() as m:
        m.get("http://192.168.1.100/get_challenge", status=200, body="challenge123")
        m.post("http://192.168.1.100/post", status=200)

        await api.send_command(command=IntelliFireCommand.POWER, value=1)


@pytest.mark.asyncio
async def test_get_challenge_returns_none_on_error(local_api):
    """Test _get_challenge returns None on various errors."""
    with patch("aiohttp.ClientSession") as session_cls:
        mock_session = session_cls.return_value
        mock_session.get = AsyncMock(side_effect=Exception("Generic error"))

        result = await local_api._get_challenge(mock_session)
        assert result is None


@pytest.mark.asyncio
async def test_background_polling_already_running(local_api):
    """Test start_background_polling when already running."""
    poll_data = {
        "temperature": 22,
        "pilot": 1,
        "power": 1,
        "serial": "TEST123",
    }

    with aioresponses() as m:
        m.get(
            "http://192.168.1.100/poll",
            status=200,
            payload=poll_data,
            repeat=True,
        )

        await local_api.start_background_polling(minimum_wait_in_seconds=1)

        await asyncio.sleep(0.2)

        assert local_api.is_polling_in_background is True

        # Try to start again while already running - should be a no-op
        await local_api.start_background_polling(minimum_wait_in_seconds=1)

        await local_api.stop_background_polling()

        await asyncio.sleep(0.1)


@pytest.mark.asyncio
async def test_stop_background_polling_not_running(local_api):
    """Test stop_background_polling when not running."""
    result = await local_api.stop_background_polling()
    assert result is False


@pytest.mark.asyncio
async def test_construct_payload_format(local_api):
    """Test _construct_payload returns correct format."""
    # Challenge must be a valid hex string
    payload = local_api._construct_payload("test_cmd", 5, "deadbeef")

    assert "command=test_cmd" in payload
    assert "value=5" in payload
    assert "user=test_user" in payload
    assert "response=" in payload


@pytest.mark.asyncio
async def test_poll_json_decode_error_suppress(local_api):
    """Test poll handles JSONDecodeError with suppress_warnings."""
    with aioresponses() as m:
        m.get(
            "http://192.168.1.100/poll",
            status=200,
            body="not valid json",
        )

        with pytest.raises(Exception):
            await local_api.poll(suppress_warnings=True)
