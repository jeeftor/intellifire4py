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
    assert "uninitialized poll data" in caplog.text


@pytest.mark.asyncio
async def test_cloud_api_send_command_warns_without_cookie(cloud_api, caplog):
    """Test warning when sending command without cookie jar."""
    cloud_api._cookie_jar = None
    with caplog.at_level("WARNING"):
        await cloud_api.send_command(command=IntelliFireCommand.POWER, value=1)
    assert "Both `api_key` and `user_id` fields must be set." in caplog.text


@pytest.mark.asyncio
async def test_cloud_api_send_command_calls_send_cloud_command(monkeypatch, cloud_api):
    """Test send_command calls _send_cloud_command."""
    monkeypatch.setattr("intellifire4py.cloud_api._range_check", lambda c, v: None)
    called = {}
    async def fake_send_cloud_command(*a, **kw):
        called["sent"] = True
        class FakeResp:
            status = 204
            async def __aenter__(self): return self
            async def __aexit__(self, exc_type, exc, tb): pass
        return FakeResp()
    monkeypatch.setattr(cloud_api, "_send_cloud_command", fake_send_cloud_command)
    # Ensure required attributes are set so method doesn't exit early
    cloud_api._cookie_jar = object()
    cloud_api.api_key = "dummy"
    cloud_api.user_id = "dummy"
    await cloud_api.send_command(command=IntelliFireCommand.POWER, value=1)
    assert called["sent"]


@pytest.mark.asyncio
async def test_cloud_api_send_cloud_command_raises_on_non_204(monkeypatch, cloud_api):
    """Test _send_cloud_command raises on non-204 response."""
    class FakeResponse:
        status = 500
        async def read(self): return b'error'
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass
        def raise_for_status(self):
            raise RuntimeError("Non-204 response")
    class FakeSession:
        def post(self, *a, **kw): return FakeResponse()
    monkeypatch.setattr(cloud_api, "_get_session", lambda *a, **kw: FakeSession())
    async def fake_convert_aiohttp_response_to_curl(r):
        return "curl ..."
    monkeypatch.setattr("intellifire4py.cloud_api._convert_aiohttp_response_to_curl", fake_convert_aiohttp_response_to_curl)
    with pytest.raises(RuntimeError):
        await cloud_api._send_cloud_command(command=IntelliFireCommand.POWER, value=1)


@pytest.mark.asyncio
async def test_cloud_api_long_poll_success(monkeypatch, cloud_api):
    """Test long poll returns valid JSON."""
    class FakeResponse:
        status = 200
        async def read(self): return b'{}'
        async def text(self): return '{}'
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass
    class FakeSession:
        async def get(self, *a, **kw): return FakeResponse()
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass
    monkeypatch.setattr(cloud_api, "_get_session", lambda *a, **kw: FakeSession())
    resp = await cloud_api.long_poll()
    assert resp is True
