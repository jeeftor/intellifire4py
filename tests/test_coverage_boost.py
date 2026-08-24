"""Additional tests to boost coverage for remaining uncovered lines."""

import pytest
import pytest_asyncio
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from aiohttp import CookieJar, ClientResponseError, RequestInfo
from aioresponses import aioresponses
from multidict import CIMultiDict, CIMultiDictProxy
from yarl import URL

from intellifire4py.cloud_api import IntelliFireAPICloud
from intellifire4py.local_api import IntelliFireAPILocal
from intellifire4py.exceptions import CloudError, CommandRetryError
from intellifire4py.const import IntelliFireCommand
from intellifire4py.udp import UDPFireplaceFinder


def _make_request_info(url: str, method: str = "GET") -> RequestInfo:
    return RequestInfo(
        url=URL(url), method=method, headers=CIMultiDictProxy(CIMultiDict())
    )


def _make_fast_time():
    """Return a time.time() mock that runs one post attempt per retry."""
    count = 0

    def fake_time():
        nonlocal count
        count += 1
        return 100.0 if count % 5 == 0 else 0.0

    return fake_time


@pytest_asyncio.fixture
async def cloud_api():
    """Create a cloud API instance for testing."""
    cookie_jar = CookieJar()
    api = IntelliFireAPICloud(
        serial="TEST123",
        use_http=False,
        verify_ssl=True,
        cookie_jar=cookie_jar,
    )
    return api


@pytest.mark.asyncio
async def test_long_poll_response_text_error(cloud_api):
    """Test long_poll when response.text() fails during error handling."""
    # Create a mock response that will fail when text() is called
    mock_response = MagicMock()
    mock_response.text = AsyncMock(side_effect=Exception("Text extraction failed"))

    # Create exception with the mock response
    exception = ClientResponseError(
        request_info=_make_request_info("https://iftapi.net/a/TEST123/applongpoll"),
        history=(),
        status=500,
    )
    exception.response = mock_response  # type: ignore

    with aioresponses() as m:
        m.get(
            "https://iftapi.net/a/TEST123/applongpoll",
            exception=exception,
        )

        with pytest.raises(CloudError, match="Unexpected status code"):
            await cloud_api.long_poll()


@pytest.mark.asyncio
async def test_local_api_poll_timeout_error():
    """Test local API poll with timeout error."""
    api = IntelliFireAPILocal(fireplace_ip="192.168.1.100")

    with aioresponses() as m:
        m.get(
            "http://192.168.1.100/poll",
            exception=asyncio.TimeoutError(),
        )

        with pytest.raises(asyncio.TimeoutError):
            await api.poll(suppress_warnings=False, timeout_seconds=1)


@pytest.mark.asyncio
async def test_local_api_send_command_challenge_timeout():
    """Test send_command when challenge retrieval times out repeatedly."""
    api = IntelliFireAPILocal(
        fireplace_ip="192.168.1.100",
        user_id="test_user",
        api_key="deadbeefdeadbeefdeadbeefdeadbeef",
    )

    with aioresponses() as m:
        # All challenge requests timeout
        m.get(
            "http://192.168.1.100/get_challenge",
            exception=asyncio.TimeoutError(),
            repeat=True,
        )

        with patch("intellifire4py.local_api.asyncio.sleep"):
            with pytest.raises(CommandRetryError):
                await api.send_command(command=IntelliFireCommand.POWER, value=1)


@pytest.mark.asyncio
async def test_local_api_send_command_post_failure():
    """Test send_command when post request fails."""
    api = IntelliFireAPILocal(
        fireplace_ip="192.168.1.100",
        user_id="test_user",
        api_key="deadbeefdeadbeefdeadbeefdeadbeef",
    )

    with aioresponses() as m:
        # Challenge succeeds
        m.get(
            "http://192.168.1.100/get_challenge",
            status=200,
            body="deadbeef",
            repeat=True,
        )
        # Post fails
        m.post(
            "http://192.168.1.100/post",
            status=500,
            repeat=True,
        )

        with patch("intellifire4py.local_api.time.time", side_effect=_make_fast_time()):
            with patch("intellifire4py.local_api.asyncio.sleep"):
                with pytest.raises(CommandRetryError):
                    await api.send_command(command=IntelliFireCommand.POWER, value=1)


@pytest.mark.asyncio
async def test_udp_finder_no_responses():
    """Test UDP finder when no fireplaces respond."""
    finder = UDPFireplaceFinder()

    # Mock socket to not receive any responses
    with patch("socket.socket") as mock_socket:
        mock_instance = MagicMock()
        mock_instance.recvfrom.side_effect = TimeoutError()
        mock_socket.return_value = mock_instance

        result = await finder.search_fireplace(timeout=0.1)
        assert result == []


@pytest.mark.asyncio
async def test_cloud_api_background_poll_already_stopped():
    """Test stopping background polling when already stopped."""
    cookie_jar = CookieJar()
    api = IntelliFireAPICloud(
        serial="TEST123",
        use_http=False,
        verify_ssl=True,
        cookie_jar=cookie_jar,
    )

    # Try to stop when not running
    result = await api.stop_background_polling()
    assert result is False

    # Try again
    result = await api.stop_background_polling()
    assert result is False


@pytest.mark.asyncio
async def test_local_api_background_poll_already_stopped():
    """Test stopping local background polling when already stopped."""
    api = IntelliFireAPILocal(fireplace_ip="192.168.1.100")

    # Try to stop when not running
    result = await api.stop_background_polling()
    assert result is False


@pytest.mark.asyncio
async def test_cloud_api_get_data_before_poll():
    """Test accessing data property before any poll."""
    cookie_jar = CookieJar()
    api = IntelliFireAPICloud(
        serial="TEST123",
        use_http=False,
        verify_ssl=True,
        cookie_jar=cookie_jar,
    )

    # Access data before polling - should return uninitialized data
    data = api.data
    assert data is not None


@pytest.mark.asyncio
async def test_local_api_get_data_before_poll():
    """Test accessing local API data property before any poll."""
    api = IntelliFireAPILocal(fireplace_ip="192.168.1.100")

    # Access data before polling
    data = api.data
    assert data is not None
