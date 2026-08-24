"""Tests targeting specific uncovered lines to push coverage higher."""

import pytest
import pytest_asyncio
from unittest.mock import MagicMock, patch
from aiohttp import CookieJar
from aioresponses import aioresponses

from intellifire4py.cloud_api import IntelliFireAPICloud
from intellifire4py.cloud_interface import IntelliFireCloudInterface
from intellifire4py.const import IntelliFireCommand
from intellifire4py.exceptions import CommandRetryError
from intellifire4py.local_api import IntelliFireAPILocal


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def local_api():
    """Create a local API instance for testing."""
    return IntelliFireAPILocal(
        fireplace_ip="192.168.1.100",
        user_id="test_user",
        api_key="deadbeefdeadbeefdeadbeefdeadbeef",
    )


@pytest_asyncio.fixture
async def cloud_api():
    """Create a cloud API instance for testing."""
    return IntelliFireAPICloud(
        serial="TEST123",
        use_http=False,
        verify_ssl=True,
        cookie_jar=CookieJar(),
    )


def _make_fast_time():
    """time.time() mock: lets the inner loop execute once, then exits.

    Call order per outer retry:
      1. _get_challenge: start        -> 0.0
      2. challenge_time =             -> 0.0
      3. first inner while check      -> 0.0  (enters: 0-0=0 < 7)
      4. second inner while check     -> 100.0 (exits: 100-0 >= 7)
    Repeats every 4 calls.
    """
    count = 0

    def fake_time():
        nonlocal count
        count += 1
        return 100.0 if count % 4 == 0 else 0.0

    return fake_time


# ---------------------------------------------------------------------------
# local_api.py — 403 / 404 / 422 status codes (lines 309, 313, 317)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_local_send_command_403_logs_warning(local_api):
    """Cover local_api.py line 309 — 403 challenge-expired warning."""
    with aioresponses() as m:
        m.get("http://192.168.1.100/get_challenge", body="deadbeef", repeat=True)
        m.post("http://192.168.1.100/post", status=403)
        m.post("http://192.168.1.100/post", status=200)

        with patch("intellifire4py.local_api.time.time", side_effect=_make_fast_time()):
            with patch.object(local_api._log, "warning") as mock_warn:
                await local_api._send_local_command(
                    command=IntelliFireCommand.POWER, value=1
                )
                assert mock_warn.called
                calls = [str(c) for c in mock_warn.call_args_list]
                assert any("403" in c for c in calls)


@pytest.mark.asyncio
async def test_local_send_command_404_logs_warning(local_api):
    """Cover local_api.py line 313 — 404 failed-post warning."""
    with aioresponses() as m:
        m.get("http://192.168.1.100/get_challenge", body="deadbeef", repeat=True)
        m.post("http://192.168.1.100/post", status=404)
        m.post("http://192.168.1.100/post", status=200)

        with patch("intellifire4py.local_api.time.time", side_effect=_make_fast_time()):
            with patch.object(local_api._log, "warning") as mock_warn:
                await local_api._send_local_command(
                    command=IntelliFireCommand.POWER, value=1
                )
                assert mock_warn.called
                calls = [str(c) for c in mock_warn.call_args_list]
                assert any("404" in c or "Failed to post" in c for c in calls)


@pytest.mark.asyncio
async def test_local_send_command_422_logs_warning(local_api):
    """Cover local_api.py line 317 — 422 warning."""
    with aioresponses() as m:
        m.get("http://192.168.1.100/get_challenge", body="deadbeef", repeat=True)
        m.post("http://192.168.1.100/post", status=422)
        m.post("http://192.168.1.100/post", status=200)

        with patch("intellifire4py.local_api.time.time", side_effect=_make_fast_time()):
            with patch.object(local_api._log, "warning") as mock_warn:
                await local_api._send_local_command(
                    command=IntelliFireCommand.POWER, value=1
                )
                assert mock_warn.called
                calls = [str(c) for c in mock_warn.call_args_list]
                assert any("422" in c for c in calls)


# ---------------------------------------------------------------------------
# local_api.py — failure log after all retries exhausted (line 344)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_local_send_command_all_retries_exhausted(local_api):
    """Cover local_api.py line 344 — failure debug log when all 10 retries fail."""
    # Return 500 on every challenge so challenge is always None -> outer loop retries 10x
    with aioresponses() as m:
        m.get("http://192.168.1.100/get_challenge", status=500, repeat=True)

        with patch("intellifire4py.local_api.asyncio.sleep"):
            with patch.object(local_api._log, "debug") as mock_debug:
                with pytest.raises(CommandRetryError):
                    await local_api._send_local_command(
                        command=IntelliFireCommand.POWER, value=1
                    )
                debug_calls = [str(c) for c in mock_debug.call_args_list]
                assert any("FAILURE" in c for c in debug_calls)


# ---------------------------------------------------------------------------
# local_api.py — __background_poll exits loop, sets flag (lines 182-183)
# Also covers stop_background_polling when task is already cancelled (131→136)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_local_background_poll_exits_and_resets_flag(local_api):
    """Cover local_api.py lines 182-183 — flag cleared after poll loop exits."""

    async def fake_poll(**kwargs):
        local_api._should_poll_in_background = False  # stop after first iteration

    with patch.object(local_api, "poll", side_effect=fake_poll):
        with patch("intellifire4py.local_api.asyncio.sleep"):
            await local_api.start_background_polling(minimum_wait_in_seconds=1)
            # Wait for the background task to actually complete
            if local_api._bg_task:
                await local_api._bg_task

    assert local_api._is_polling_in_background is False


@pytest.mark.asyncio
async def test_local_stop_background_polling_already_cancelled(local_api):
    """Cover local_api.py branch 131→136 — stop when task is already cancelled."""
    mock_task = MagicMock()
    mock_task.cancelled.return_value = True
    local_api._bg_task = mock_task
    local_api._should_poll_in_background = True

    result = await local_api.stop_background_polling()

    assert result is False
    mock_task.cancel.assert_not_called()


# ---------------------------------------------------------------------------
# cloud_api.py — stop_background_polling already-cancelled branch (330→334)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cloud_stop_background_polling_already_cancelled(cloud_api):
    """Cover cloud_api.py branch 330→334 — stop when task is already cancelled."""
    mock_task = MagicMock()
    mock_task.cancelled.return_value = True
    cloud_api._bg_task = mock_task
    cloud_api._should_poll_in_background = True

    result = await cloud_api.stop_background_polling()

    assert result is False
    mock_task.cancel.assert_not_called()


# ---------------------------------------------------------------------------
# cloud_api.py — __background_poll exception path (lines 376-378)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cloud_background_poll_exception_and_exit(cloud_api):
    """Cover cloud_api.py lines 376-378 — exception logged, loop exits cleanly."""
    call_count = 0

    async def fake_poll():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise RuntimeError("simulated poll failure")
        cloud_api._should_poll_in_background = False

    with patch.object(cloud_api, "poll", side_effect=fake_poll):
        with patch("intellifire4py.cloud_api.asyncio.sleep"):
            with patch.object(cloud_api, "_poll_mode") as mock_mode:
                from intellifire4py.const import IntelliFireCloudPollType

                mock_mode.__eq__ = lambda s, o: o != IntelliFireCloudPollType.LONG
                cloud_api._should_poll_in_background = True
                # Call the private method directly via name mangling
                await cloud_api._IntelliFireAPICloud__background_poll(
                    minimum_wait_in_seconds=1
                )

    assert cloud_api._is_polling_in_background is False


# ---------------------------------------------------------------------------
# cloud_interface.py — login with no session raises RuntimeError (line 188)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cloud_interface_login_no_session_raises():
    """Cover cloud_interface.py line 188 — RuntimeError when session is None but in context."""
    iface = IntelliFireCloudInterface()
    iface._session = None
    iface._in_context = True  # bypass the context-guard to reach the session check

    with pytest.raises(RuntimeError, match="Session is not initialized"):
        await iface.login_with_credentials(
            username="user@example.com", password="secret"
        )


# ---------------------------------------------------------------------------
# cloud_interface.py — __aexit__ with open session closes it (88→exit branch)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cloud_interface_aexit_closes_session():
    """Cover cloud_interface.py branch 88→exit — close_session when session is open."""
    async with IntelliFireCloudInterface() as iface:
        assert iface._session is not None
    # After context exit the session should be closed
    assert iface._session.closed


# ---------------------------------------------------------------------------
# cloud_api.py — line 165: non-204 2xx raises exception (e.g. status 200)
# raise_for_status() only raises on 4xx/5xx, so 200 reaches the else branch.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cloud_send_command_200_raises(cloud_api):
    """Cover cloud_api.py line 165 — non-204 2xx status raises exception."""
    with aioresponses() as m:
        m.post(
            "https://iftapi.net/a/TEST123//apppost",
            status=200,
        )
        with pytest.raises(Exception, match="Unexpected return code 200"):
            await cloud_api._send_cloud_command(
                command=IntelliFireCommand.POWER, value=1
            )
