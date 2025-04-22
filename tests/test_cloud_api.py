"""Test cloud functions."""

import pytest
from aioresponses import aioresponses
from unittest.mock import patch
from intellifire4py.cloud_api import IntelliFireAPICloud, IntelliFireCommand
import aiohttp
from aiohttp import CookieJar


@pytest.fixture
def cloud_api():
    # Provide a real instance for testing
    cookie_jar = CookieJar()
    return IntelliFireAPICloud(serial="ABC123", cookie_jar=cookie_jar)


@pytest.mark.asyncio
async def test_send_cloud_command_204(cloud_api):
    url = f"{cloud_api.prefix}://iftapi.net/a/{cloud_api._serial}//apppost"
    with aioresponses() as m:
        m.post(url, status=204)
        await cloud_api._send_cloud_command(command=IntelliFireCommand.POWER, value=1)
        # No exception means pass


@pytest.mark.asyncio
async def test_send_cloud_command_raises_403(cloud_api):
    url = f"{cloud_api.prefix}://iftapi.net/a/{cloud_api._serial}//apppost"
    with aioresponses() as m:
        m.post(url, status=403)
        with pytest.raises(aiohttp.ClientResponseError):
            await cloud_api._send_cloud_command(command=IntelliFireCommand.POWER, value=1)


@pytest.mark.asyncio
async def test_send_cloud_command_logs_debug(cloud_api):
    url = f"{cloud_api.prefix}://iftapi.net/a/{cloud_api._serial}//apppost"
    with aioresponses() as m:
        m.post(url, status=204)
        with patch.object(cloud_api._log, "debug") as log_debug:
            await cloud_api._send_cloud_command(command=IntelliFireCommand.POWER, value=1)
            log_debug.assert_called()
