"""Extended tests for cloud_api.py to improve coverage."""

import pytest
import json
import pytest_asyncio
from aiohttp import CookieJar, ClientResponseError
from aioresponses import aioresponses

from intellifire4py.cloud_api import IntelliFireAPICloud
from intellifire4py.exceptions import CloudError
from intellifire4py.const import IntelliFireCloudPollType, IntelliFireCommand
from intellifire4py.model import IntelliFirePollData


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
async def test_long_poll_200_success(cloud_api):
    """Test long_poll with 200 status code (data changed)."""
    poll_data = {
        "temperature": 22,
        "pilot": 1,
        "power": 1,
        "serial": "TEST123",
    }

    with aioresponses() as m:
        m.get(
            "https://iftapi.net/a/TEST123/applongpoll",
            status=200,
            body=json.dumps(poll_data),
            headers={"Content-Type": "text/html"},
        )

        result = await cloud_api.long_poll()
        assert result is True
        assert cloud_api.data.temperature_c == 22


@pytest.mark.asyncio
async def test_long_poll_408_no_change(cloud_api):
    """Test long_poll with 408 status code (no data changed)."""
    with aioresponses() as m:
        m.get(
            "https://iftapi.net/a/TEST123/applongpoll",
            status=408,
        )

        result = await cloud_api.long_poll()
        assert result is False


@pytest.mark.asyncio
async def test_long_poll_403_not_authorized(cloud_api):
    """Test long_poll with 403 status code (not authorized)."""
    from aiohttp import ClientResponseError, RequestInfo
    
    with aioresponses() as m:
        m.get(
            "https://iftapi.net/a/TEST123/applongpoll",
            exception=ClientResponseError(
                request_info=RequestInfo(url="https://iftapi.net/a/TEST123/applongpoll", method="GET", headers={}),
                history=(),
                status=403,
            ),
        )

        with pytest.raises(CloudError, match="Not authorized"):
            await cloud_api.long_poll()


@pytest.mark.asyncio
async def test_long_poll_404_not_found(cloud_api):
    """Test long_poll with 404 status code (fireplace not found)."""
    from aiohttp import ClientResponseError, RequestInfo
    
    with aioresponses() as m:
        m.get(
            "https://iftapi.net/a/TEST123/applongpoll",
            exception=ClientResponseError(
                request_info=RequestInfo(url="https://iftapi.net/a/TEST123/applongpoll", method="GET", headers={}),
                history=(),
                status=404,
            ),
        )

        with pytest.raises(CloudError, match="Fireplace not found"):
            await cloud_api.long_poll()


@pytest.mark.asyncio
async def test_long_poll_unexpected_status(cloud_api):
    """Test long_poll with unexpected status code."""
    from aiohttp import ClientResponseError, RequestInfo
    
    with aioresponses() as m:
        m.get(
            "https://iftapi.net/a/TEST123/applongpoll",
            exception=ClientResponseError(
                request_info=RequestInfo(url="https://iftapi.net/a/TEST123/applongpoll", method="GET", headers={}),
                history=(),
                status=500,
            ),
        )

        with pytest.raises(CloudError, match="Unexpected status code"):
            await cloud_api.long_poll()


@pytest.mark.asyncio
async def test_send_command_no_cookie_jar():
    """Test send_command when cookie_jar is not set."""
    api = IntelliFireAPICloud(
        serial="TEST123",
        use_http=False,
        verify_ssl=True,
        cookie_jar=None,
    )

    await api.send_command(command=IntelliFireCommand.POWER, value=1)


@pytest.mark.asyncio
async def test_send_cloud_command_unexpected_status(cloud_api):
    """Test _send_cloud_command with unexpected status code."""
    with aioresponses() as m:
        m.post(
            "https://iftapi.net/a/TEST123//apppost",
            status=500,
        )

        with pytest.raises(ClientResponseError):
            await cloud_api._send_cloud_command(
                command=IntelliFireCommand.POWER, value=1
            )


@pytest.mark.asyncio
async def test_poll_403_not_authorized(cloud_api):
    """Test poll with 403 status code."""
    from aiohttp import ClientResponseError, RequestInfo
    
    with aioresponses() as m:
        m.get(
            "https://iftapi.net/a/TEST123//apppoll",
            exception=ClientResponseError(
                request_info=RequestInfo(url="https://iftapi.net/a/TEST123//apppoll", method="GET", headers={}),
                history=(),
                status=403,
            ),
        )

        with pytest.raises(ClientResponseError):
            await cloud_api.poll()


@pytest.mark.asyncio
async def test_poll_404_not_found(cloud_api):
    """Test poll with 404 status code."""
    from aiohttp import ClientResponseError, RequestInfo
    
    with aioresponses() as m:
        m.get(
            "https://iftapi.net/a/TEST123//apppoll",
            exception=ClientResponseError(
                request_info=RequestInfo(url="https://iftapi.net/a/TEST123//apppoll", method="GET", headers={}),
                history=(),
                status=404,
            ),
        )

        with pytest.raises(ClientResponseError):
            await cloud_api.poll()


@pytest.mark.asyncio
async def test_background_poll_short_mode(cloud_api):
    """Test background polling with SHORT poll mode."""
    import asyncio
    
    cloud_api.set_poll_mode(IntelliFireCloudPollType.SHORT)

    poll_data = {
        "temperature": 22,
        "pilot": 1,
        "power": 1,
        "serial": "TEST123",
    }

    with aioresponses() as m:
        m.get(
            "https://iftapi.net/a/TEST123//apppoll",
            status=200,
            payload=poll_data,
            repeat=True,
        )

        await cloud_api.start_background_polling(minimum_wait_in_seconds=1)

        await asyncio.sleep(0.2)

        assert cloud_api.is_polling_in_background is True

        await cloud_api.stop_background_polling()


@pytest.mark.asyncio
async def test_background_poll_exception_handling(cloud_api):
    """Test background polling handles exceptions gracefully."""
    import asyncio
    
    # Set to SHORT mode so it uses poll() which uses //apppoll URL
    cloud_api.set_poll_mode(IntelliFireCloudPollType.SHORT)
    
    poll_data = {
        "temperature": 22,
        "pilot": 1,
        "power": 1,
        "serial": "TEST123",
    }
    
    with aioresponses() as m:
        # First call succeeds to start polling
        m.get(
            "https://iftapi.net/a/TEST123//apppoll",
            status=200,
            payload=poll_data,
        )
        # Subsequent calls fail with exception
        m.get(
            "https://iftapi.net/a/TEST123//apppoll",
            exception=Exception("Test exception"),
            repeat=True,
        )

        await cloud_api.start_background_polling(minimum_wait_in_seconds=1)

        await asyncio.sleep(0.5)

        # Should still be running despite exceptions
        assert cloud_api.is_polling_in_background is True

        await cloud_api.stop_background_polling()


@pytest.mark.asyncio
async def test_stop_background_polling_when_not_running(cloud_api):
    """Test stop_background_polling when not running."""
    result = await cloud_api.stop_background_polling()
    assert result is False


@pytest.mark.asyncio
async def test_get_data_uninitialized_warning(cloud_api):
    """Test get_data returns uninitialized data warning."""
    data = cloud_api.get_data()
    assert isinstance(data, IntelliFirePollData)


def test_set_poll_mode(cloud_api):
    """Test set_poll_mode changes the poll mode."""
    cloud_api.set_poll_mode(IntelliFireCloudPollType.SHORT)
    assert cloud_api._poll_mode == IntelliFireCloudPollType.SHORT

    cloud_api.set_poll_mode(IntelliFireCloudPollType.LONG)
    assert cloud_api._poll_mode == IntelliFireCloudPollType.LONG
