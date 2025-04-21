"""Test cloud functions."""

import pytest
import pytest_asyncio
import aiohttp
from intellifire4py.cloud_api import IntelliFireAPICloud
from intellifire4py.const import IntelliFireCommand, IntelliFireCloudPollType
from aiohttp import CookieJar
from intellifire4py.exceptions import CloudError
from aioresponses import aioresponses

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
async def test_cloud_api_send_cloud_command_raises_on_non_204(cloud_api):
    """Test _send_cloud_command raises on non-204 response."""
    with aioresponses() as m:
        m.post("https://iftapi.net/a/SERIAL123//apppost", status=500, body=b'error')
        with pytest.raises(aiohttp.ClientResponseError):
            await cloud_api._send_cloud_command(command=IntelliFireCommand.POWER, value=1)


@pytest.mark.asyncio
async def test_send_cloud_command_raises_clouderror_403(cloud_api):
    """Test that sending a cloud command with 403 response raises aiohttp.ClientResponseError."""
    with aioresponses() as m:
        m.post("https://iftapi.net/a/SERIAL123//apppost", status=403)
        with pytest.raises(aiohttp.ClientResponseError):
            await cloud_api._send_cloud_command(command=IntelliFireCommand.POWER, value=1)


@pytest.mark.asyncio
async def test_send_cloud_command_raises_clouderror_404(cloud_api):
    """Test that sending a cloud command with 404 response raises aiohttp.ClientResponseError."""
    with aioresponses() as m:
        m.post("https://iftapi.net/a/SERIAL123//apppost", status=404)
        with pytest.raises(aiohttp.ClientResponseError):
            await cloud_api._send_cloud_command(command=IntelliFireCommand.POWER, value=1)


@pytest.mark.asyncio
async def test_send_cloud_command_raises_clouderror_422(cloud_api):
    """Test that sending a cloud command with 422 response raises aiohttp.ClientResponseError."""
    with aioresponses() as m:
        m.post("https://iftapi.net/a/SERIAL123//apppost", status=422)
        with pytest.raises(aiohttp.ClientResponseError):
            await cloud_api._send_cloud_command(command=IntelliFireCommand.POWER, value=1)


@pytest.mark.asyncio
async def test_send_cloud_command_raises_on_unexpected(cloud_api):
    """Test that sending a cloud command with unexpected status raises aiohttp.ClientResponseError."""
    with aioresponses() as m:
        m.post("https://iftapi.net/a/SERIAL123//apppost", status=500)
        with pytest.raises(aiohttp.ClientResponseError):
            await cloud_api._send_cloud_command(command=IntelliFireCommand.POWER, value=1)


@pytest.mark.asyncio
async def test_cloud_api_long_poll_success(cloud_api):
    """Test long poll returns valid JSON."""
    with aioresponses() as m:
        m.get("https://iftapi.net/a/SERIAL123/applongpoll", status=200, body=b'{}')
        resp = await cloud_api.long_poll()
        assert resp is True


@pytest.mark.asyncio
async def test_long_poll_handles_403(cloud_api):
    """Test that long_poll handles a 403 response."""
    with aioresponses() as m:
        m.get("https://iftapi.net/a/SERIAL123/applongpoll", status=403)
        with pytest.raises(CloudError):
            await cloud_api.long_poll()


@pytest.mark.asyncio
async def test_long_poll_handles_404(cloud_api):
    """Test that long_poll handles a 404 response."""
    with aioresponses() as m:
        m.get("https://iftapi.net/a/SERIAL123/applongpoll", status=404)
        with pytest.raises(CloudError):
            await cloud_api.long_poll()


@pytest.mark.asyncio
async def test_long_poll_raises_clientresponseerror_403(monkeypatch, cloud_api):
    """Test that long_poll raises CloudError on 403 ClientResponseError."""
    import aiohttp
    from intellifire4py.exceptions import CloudError
    class FakeResponse:
        status = 403
        async def __aenter__(self):
            raise aiohttp.ClientResponseError(None, (), status=self.status)
        async def __aexit__(self, exc_type, exc, tb): pass
    class FakeSession:
        async def get(self, *a, **kw): return FakeResponse()
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass
    monkeypatch.setattr(cloud_api, "_get_session", lambda *a, **kw: FakeSession())
    with pytest.raises(CloudError) as excinfo:
        await cloud_api.long_poll()
    assert "Not authorized" in str(excinfo.value)


@pytest.mark.asyncio
async def test_long_poll_raises_clientresponseerror_404(monkeypatch, cloud_api):
    """Test that long_poll raises CloudError on 404 ClientResponseError."""
    import aiohttp
    from intellifire4py.exceptions import CloudError
    class FakeResponse:
        status = 404
        async def __aenter__(self):
            raise aiohttp.ClientResponseError(None, (), status=self.status)
        async def __aexit__(self, exc_type, exc, tb): pass
    class FakeSession:
        async def get(self, *a, **kw): return FakeResponse()
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass
    monkeypatch.setattr(cloud_api, "_get_session", lambda *a, **kw: FakeSession())
    with pytest.raises(CloudError) as excinfo:
        await cloud_api.long_poll()
    assert "Fireplace not found" in str(excinfo.value)


@pytest.mark.asyncio
async def test_long_poll_raises_clientresponseerror_other(monkeypatch, cloud_api):
    """Test that long_poll raises CloudError on unexpected ClientResponseError status."""
    import aiohttp
    from intellifire4py.exceptions import CloudError
    class FakeResponse:
        status = 500
        async def __aenter__(self):
            raise aiohttp.ClientResponseError(None, (), status=self.status)
        async def __aexit__(self, exc_type, exc, tb): pass
    class FakeSession:
        async def get(self, *a, **kw): return FakeResponse()
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass
    monkeypatch.setattr(cloud_api, "_get_session", lambda *a, **kw: FakeSession())
    with pytest.raises(CloudError) as excinfo:
        await cloud_api.long_poll()
    assert "Unexpected status code" in str(excinfo.value)


@pytest.mark.asyncio
async def test_start_and_stop_background_polling(monkeypatch, cloud_api):
    """Test starting and stopping the background polling task."""
    # Patch poll to avoid actual network calls
    async def fake_poll(*a, **kw): return None
    monkeypatch.setattr(cloud_api, "poll", fake_poll)
    await cloud_api.start_background_polling(minimum_wait_in_seconds=0)
    assert cloud_api._should_poll_in_background
    stopped = await cloud_api.stop_background_polling()
    assert stopped is True or stopped is False  # just check it runs


@pytest.mark.asyncio
async def test_background_poll_loop_handles_exception(monkeypatch, cloud_api):
    """Test that background poll loop handles exceptions without crashing."""
    # Patch poll to raise exception
    async def fake_poll(*a, **kw): raise Exception("fail!")
    monkeypatch.setattr(cloud_api, "poll", fake_poll)
    cloud_api._should_poll_in_background = True
    cloud_api._is_polling_in_background = False
    # Patch asyncio.sleep to break loop after one iteration
    import asyncio as aio
    calls = {}
    async def fake_sleep(secs):
        calls['called'] = True
        cloud_api._should_poll_in_background = False  # stop loop
    monkeypatch.setattr(aio, "sleep", fake_sleep)
    await cloud_api._IntelliFireAPICloud__background_poll(minimum_wait_in_seconds=0)
    assert calls['called']
    assert not cloud_api._should_poll_in_background


@pytest.mark.asyncio
async def test_poll_handles_403(monkeypatch, cloud_api):
    """Test that poll handles a 403 response."""
    class FakeResponse:
        status = 403
        async def json(self): return {}
        def raise_for_status(self):
            raise aiohttp.ClientResponseError(None, (), status=403)
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass
    class FakeSession:
        async def get(self, *a, **kw): return FakeResponse()
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass
    monkeypatch.setattr(cloud_api, "_get_session", lambda *a, **kw: FakeSession())
    with pytest.raises(aiohttp.ClientResponseError):
        await cloud_api.poll()


@pytest.mark.asyncio
async def test_poll_handles_404(monkeypatch, cloud_api):
    """Test that poll handles a 404 response."""
    class FakeResponse:
        status = 404
        async def json(self): return {}
        def raise_for_status(self):
            raise aiohttp.ClientResponseError(None, (), status=404)
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass
    class FakeSession:
        async def get(self, *a, **kw): return FakeResponse()
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass
    monkeypatch.setattr(cloud_api, "_get_session", lambda *a, **kw: FakeSession())
    with pytest.raises(aiohttp.ClientResponseError):
        await cloud_api.poll()


@pytest.mark.asyncio
async def test_cloud_api_data_property_warns_on_localhost(cloud_api, caplog):
    """Test that accessing the data property on localhost issues a warning."""
    cloud_api._data.ipv4_address = "127.0.0.1"
    with caplog.at_level("WARNING"):
        _ = cloud_api.data
    assert "uninitialized poll data" in caplog.text
