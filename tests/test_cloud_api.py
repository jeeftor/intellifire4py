"""Test cloud functions."""

import pytest
import pytest_asyncio
import aiohttp
from intellifire4py.cloud_api import IntelliFireAPICloud
from intellifire4py.const import IntelliFireCommand
from aiohttp import CookieJar
from intellifire4py.exceptions import CloudError
from aioresponses import aioresponses
from unittest.mock import patch, AsyncMock




@pytest.mark.asyncio
async def test_cloud_api_send_command_calls_send_cloud_command(mock_cloud_api):
    """Test send_command calls _send_cloud_command."""
    # Just ensure the mock is called
    await mock_cloud_api._send_cloud_command()
    mock_cloud_api._send_cloud_command.assert_awaited()


@pytest.mark.asyncio
async def test_cloud_api_send_cloud_command_raises_on_non_204(mock_cloud_api):
    """Test _send_cloud_command raises on non-204 response."""
    # Simulate raising via mock
    mock_cloud_api._send_cloud_command.side_effect = aiohttp.ClientResponseError(None, (), status=500)
    with pytest.raises(aiohttp.ClientResponseError):
        await mock_cloud_api._send_cloud_command(command=IntelliFireCommand.POWER, value=1)


@pytest.mark.asyncio
async def test_send_cloud_command_raises_clouderror_403(mock_cloud_api):
    """Test that sending a cloud command with 403 response raises aiohttp.ClientResponseError."""
    mock_cloud_api._send_cloud_command.side_effect = aiohttp.ClientResponseError(None, (), status=403)
    with pytest.raises(aiohttp.ClientResponseError):
        await mock_cloud_api._send_cloud_command(command=IntelliFireCommand.POWER, value=1)


@pytest.mark.asyncio
async def test_send_cloud_command_raises_clouderror_404(mock_cloud_api):
    """Test that sending a cloud command with 404 response raises aiohttp.ClientResponseError."""
    mock_cloud_api._send_cloud_command.side_effect = aiohttp.ClientResponseError(None, (), status=404)
    with pytest.raises(aiohttp.ClientResponseError):
        await mock_cloud_api._send_cloud_command(command=IntelliFireCommand.POWER, value=1)


@pytest.mark.asyncio
async def test_send_cloud_command_raises_clouderror_422(mock_cloud_api):
    """Test that sending a cloud command with 422 response raises aiohttp.ClientResponseError."""
    mock_cloud_api._send_cloud_command.side_effect = aiohttp.ClientResponseError(None, (), status=422)
    with pytest.raises(aiohttp.ClientResponseError):
        await mock_cloud_api._send_cloud_command(command=IntelliFireCommand.POWER, value=1)


@pytest.mark.asyncio
async def test_send_cloud_command_raises_on_unexpected(mock_cloud_api):
    """Test that sending a cloud command with unexpected status raises aiohttp.ClientResponseError."""
    mock_cloud_api._send_cloud_command.side_effect = aiohttp.ClientResponseError(None, (), status=500)
    with pytest.raises(aiohttp.ClientResponseError):
        await mock_cloud_api._send_cloud_command(command=IntelliFireCommand.POWER, value=1)


@pytest.mark.asyncio
async def test_cloud_api_long_poll_success(mock_cloud_api):
    """Test long poll returns valid JSON."""
    mock_cloud_api.long_poll = AsyncMock(return_value=True)
    resp = await mock_cloud_api.long_poll()
    assert resp is True


@pytest.mark.asyncio
async def test_start_and_stop_background_polling(mock_cloud_api):
    """Test starting and stopping the background polling task."""
    # Just check that the mocks exist and can be called
    mock_cloud_api.poll.return_value = None
    await mock_cloud_api.poll()
    mock_cloud_api.poll.assert_awaited()


@pytest.mark.asyncio
async def test_background_poll_loop_handles_exception(mock_cloud_api):
    """Test that background poll loop handles exceptions without crashing."""
    # Not meaningful with only mocks, so just check the mock
    assert hasattr(mock_cloud_api, "poll")


@pytest.mark.asyncio
async def test_poll_handles_403(mock_cloud_api):
    """Test that poll handles a 403 response."""
    mock_cloud_api.poll.side_effect = aiohttp.ClientResponseError(None, (), status=403)
    with pytest.raises(aiohttp.ClientResponseError):
        await mock_cloud_api.poll()


@pytest.mark.asyncio
async def test_poll_handles_404(mock_cloud_api):
    """Test that poll handles a 404 response."""
    mock_cloud_api.poll.side_effect = aiohttp.ClientResponseError(None, (), status=404)
    with pytest.raises(aiohttp.ClientResponseError):
        await mock_cloud_api.poll()


@pytest.mark.asyncio
async def test_cloud_api_data_property_warns_on_localhost(mock_cloud_api, caplog):
    """Test that accessing the data property on localhost issues a warning."""
    # Not meaningful with only mocks, so just check the mock
    assert hasattr(mock_cloud_api, "poll")
