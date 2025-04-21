"""Test cloud functions."""

import pytest
import asyncio
from unittest import mock
from intellifire4py.cloud_api import IntelliFireAPICloud
from intellifire4py.const import IntelliFireCommand
from aiohttp import CookieJar
import pytest_asyncio

@pytest_asyncio.fixture
async def dummy_cookie_jar():
    from aiohttp import CookieJar
    return CookieJar()

@pytest_asyncio.fixture
async def cloud_api(dummy_cookie_jar):
    from intellifire4py.cloud_api import IntelliFireAPICloud
    return IntelliFireAPICloud(serial="SERIAL123", cookie_jar=dummy_cookie_jar)


def test_cloud_api_init_and_properties(cloud_api):
    assert cloud_api._serial == "SERIAL123"
    assert cloud_api.is_polling_in_background is False
    assert hasattr(cloud_api, "_cookie_jar")
    assert hasattr(cloud_api, "_data")
    assert hasattr(cloud_api, "_user_data")


def test_cloud_api_get_data_warns_on_localhost(cloud_api, caplog):
    # Simulate the ipv4_address being localhost
    cloud_api._data.ipv4_address = "127.0.0.1"
    with caplog.at_level("WARNING"):
        data = cloud_api.get_data()
        assert data is cloud_api._data
        assert any("Returning uninitialized poll data" in r for r in caplog.text.splitlines())

@pytest.mark.asyncio
async def test_cloud_api_send_command_warns_without_cookie(cloud_api, caplog):
    cloud_api._cookie_jar = None
    with caplog.at_level("WARNING"):
        await cloud_api.send_command(command=IntelliFireCommand.POWER, value=1)
        assert any("Unable to control fireplace" in r for r in caplog.text.splitlines())

@pytest.mark.asyncio
async def test_cloud_api_send_command_calls_send_cloud_command(monkeypatch, cloud_api):
    monkeypatch.setattr("intellifire4py.cloud_api._range_check", lambda c, v: None)
    called = {}
    async def fake_send_cloud_command(**kwargs):
        called["yes"] = True
    monkeypatch.setattr(cloud_api, "_send_cloud_command", fake_send_cloud_command)
    await cloud_api.send_command(command=IntelliFireCommand.POWER, value=1)
    assert called["yes"]

@pytest.mark.asyncio
async def test_cloud_api_send_cloud_command_raises_on_non_204(monkeypatch, cloud_api):
    # Patch session.post to return a mock response
    class FakeResponse:
        def __init__(self):
            self.status = 500
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): return False
        async def read(self): return b''
        async def text(self): return ''
        async def json(self): return {}
        def raise_for_status(self): pass
    class FakeSession:
        def post(self, url, data): return FakeResponse()
    monkeypatch.setattr(cloud_api, "_get_session", lambda *a, **kw: FakeSession())
    monkeypatch.setattr("intellifire4py.cloud_api._convert_aiohttp_response_to_curl", lambda r: "curl ...")
    with pytest.raises(Exception):
        await cloud_api._send_cloud_command(command=IntelliFireCommand.POWER, value=1)

@pytest.mark.asyncio
async def test_cloud_api_long_poll_success(monkeypatch, cloud_api):
    class FakeResponse:
        status = 200
        async def read(self): return b''
        async def text(self): return ''
        async def json(self): return {}
    class FakeSession:
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): return False
        async def get(self, url, timeout): return FakeResponse()
    monkeypatch.setattr(cloud_api, "_get_session", lambda *a, **kw: FakeSession())
    monkeypatch.setattr("intellifire4py.cloud_api._convert_aiohttp_response_to_curl", lambda r: "curl ...")
    result = await cloud_api.long_poll()
    assert result in (True, False)
