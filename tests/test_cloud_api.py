"""Test cloud functions."""

import pytest
import pytest_asyncio
from intellifire4py.cloud_api import IntelliFireAPICloud
from intellifire4py.const import IntelliFireCommand
from aiohttp import CookieJar

@pytest_asyncio.fixture
async def dummy_cookie_jar():
    """Fixture for a dummy aiohttp CookieJar."""
    return CookieJar()

@pytest_asyncio.fixture
async def cloud_api(dummy_cookie_jar):
    """Fixture for IntelliFireAPICloud with dummy cookie jar."""
    return IntelliFireAPICloud(serial="SERIAL123", cookie_jar=dummy_cookie_jar)


def test_cloud_api_init_and_properties(cloud_api):
    """Test initialization and properties of IntelliFireAPICloud."""
    assert cloud_api._serial == "SERIAL123"
    assert cloud_api.is_polling_in_background is False
    assert hasattr(cloud_api, "_cookie_jar")
    assert hasattr(cloud_api, "_data")
    assert hasattr(cloud_api, "_user_data")


def test_cloud_api_get_data_warns_on_localhost(cloud_api, caplog):
    """Test warning when ipv4_address is localhost."""
    # Simulate the ipv4_address being localhost
    cloud_api._data.ipv4_address = "127.0.0.1"
    with caplog.at_level("WARNING"):
        _ = cloud_api.get_data()
    assert "localhost" in caplog.text


@pytest.mark.asyncio
async def test_cloud_api_send_command_warns_without_cookie(cloud_api, caplog):
    """Test warning when sending command without cookie jar."""
    cloud_api._cookie_jar = None
    with caplog.at_level("WARNING"):
        await cloud_api.send_command(IntelliFireCommand.POWER, 1)
    assert "cookie jar" in caplog.text


@pytest.mark.asyncio
async def test_cloud_api_send_command_calls_send_cloud_command(monkeypatch, cloud_api):
    """Test send_command calls _send_cloud_command."""
    monkeypatch.setattr("intellifire4py.cloud_api._range_check", lambda c, v: None)
    called = {}
    async def fake_send_cloud_command(*a, **kw):
        called["sent"] = True
        class FakeResp:
            status = 204
        return FakeResp()
    monkeypatch.setattr(cloud_api, "_send_cloud_command", fake_send_cloud_command)
    await cloud_api.send_command(IntelliFireCommand.POWER, 1)
    assert called["sent"]


@pytest.mark.asyncio
async def test_cloud_api_send_cloud_command_raises_on_non_204(monkeypatch, cloud_api):
    """Test _send_cloud_command raises on non-204 response."""
    # Patch session.post to return a mock response
    class FakeResponse:
        status = 500
        async def read(self): return b'error'
    class FakeSession:
        async def post(self, *a, **kw): return FakeResponse()
    monkeypatch.setattr(cloud_api, "_get_session", lambda *a, **kw: FakeSession())
    monkeypatch.setattr("intellifire4py.cloud_api._convert_aiohttp_response_to_curl", lambda r: "curl ...")
    with pytest.raises(Exception):
        await cloud_api._send_cloud_command(command=IntelliFireCommand.POWER, value=1)


@pytest.mark.asyncio
async def test_cloud_api_long_poll_success(monkeypatch, cloud_api):
    """Test long poll returns valid JSON."""
    class FakeResponse:
        status = 200
        async def read(self): return b'{}'
    class FakeSession:
        async def get(self, *a, **kw): return FakeResponse()
    monkeypatch.setattr(cloud_api, "_get_session", lambda *a, **kw: FakeSession())
    resp = await cloud_api.long_poll()
    assert resp == {}
