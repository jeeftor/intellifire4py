"""Final push to get coverage to 97%+ by targeting remaining uncovered lines."""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from aiohttp import CookieJar
from aioresponses import aioresponses

from intellifire4py.cloud_api import IntelliFireAPICloud
from intellifire4py.const import IntelliFireCommand, IntelliFireApiMode
from intellifire4py.local_api import IntelliFireAPILocal
from intellifire4py.model import IntelliFireCommonFireplaceData
from intellifire4py.unified_fireplace import UnifiedFireplace


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


@pytest.fixture
def local_api():
    """Create a local API instance for testing."""
    return IntelliFireAPILocal(
        fireplace_ip="192.168.1.100",
        user_id="test_user",
        api_key="deadbeefdeadbeefdeadbeefdeadbeef",
    )


# ============================================================================
# cloud_api.py - Line 165: Unexpected status code
# ============================================================================


@pytest.mark.asyncio
async def test_cloud_send_command_unexpected_status(cloud_api):
    """Test _send_cloud_command raises exception for unexpected status code (line 165)."""
    with aioresponses() as m:
        # Mock 418 I'm a teapot - unexpected status
        m.post(
            "https://iftapi.net/a/c",
            status=418,
        )

        with pytest.raises(Exception):
            await cloud_api._send_cloud_command(command="power", value=1)


# ============================================================================
# cloud_api.py - Line 236: Long poll returns False on unexpected status
# ============================================================================


@pytest.mark.asyncio
async def test_cloud_long_poll_unexpected_status_returns_false(cloud_api):
    """Test long_poll returns False on unexpected status code (line 236)."""
    with aioresponses() as m:
        # Mock 500 server error - should return False
        m.get(
            "https://iftapi.net/a/TEST123/applongpoll",
            status=500,
        )

        result = await cloud_api.long_poll()
        assert result is False


# ============================================================================
# local_api.py - Line 277: Challenge timeout/error continue
# ============================================================================


@pytest.mark.asyncio
async def test_local_send_command_challenge_failure_retry(local_api):
    """Test _send_local_command retries when challenge fails (line 277)."""
    with aioresponses() as m:
        # First challenge fails (returns None)
        m.get(
            "http://192.168.1.100/get_challenge",
            status=500,
        )
        # Second challenge succeeds - returns just the hex string
        m.get(
            "http://192.168.1.100/get_challenge",
            body="deadbeef",  # Challenge is returned as plain text, not JSON
        )
        # Post succeeds
        m.post(
            "http://192.168.1.100/post",
            status=200,
        )

        await local_api._send_local_command(command=IntelliFireCommand.POWER, value=1)

        # Should have retried after first challenge failure


# ============================================================================
# local_api.py - Lines 327-329: Unexpected status code warning
# ============================================================================


@pytest.mark.asyncio
async def test_local_send_command_unexpected_status_logs_warning(local_api):
    """Test _send_local_command logs warning for unexpected status (lines 327-329)."""
    with aioresponses() as m:
        m.get(
            "http://192.168.1.100/get_challenge",
            body="deadbeef",  # Plain text response
            repeat=True,
        )
        # Return unexpected status code
        m.post(
            "http://192.168.1.100/post",
            status=418,
            repeat=True,
        )

        with patch.object(local_api._log, "warning") as mock_warning:
            await local_api._send_local_command(
                command=IntelliFireCommand.POWER, value=1
            )

            # Should log warning about unexpected status
            assert mock_warning.called
            # Check that warning mentions unexpected response
            warning_calls = [str(call) for call in mock_warning.call_args_list]
            assert any("Unexpected Response Code" in call for call in warning_calls)


# ============================================================================
# local_api.py - Lines 330-332: TimeoutError handling
# ============================================================================


@pytest.mark.asyncio
async def test_local_send_command_timeout_error_retry(local_api):
    """Test _send_local_command handles TimeoutError and retries (lines 330-332)."""
    with aioresponses() as m:
        m.get(
            "http://192.168.1.100/get_challenge",
            body="deadbeef",
            repeat=True,
        )
        # First post times out
        m.post(
            "http://192.168.1.100/post",
            exception=TimeoutError("Connection timeout"),
        )
        # Second post succeeds
        m.post(
            "http://192.168.1.100/post",
            status=200,
        )

        with patch.object(local_api._log, "warning") as mock_warning:
            await local_api._send_local_command(
                command=IntelliFireCommand.POWER, value=1
            )

            # Should log timeout warning
            assert mock_warning.called


# ============================================================================
# local_api.py - Lines 333-335: Unhandled exception logging
# ============================================================================


@pytest.mark.asyncio
async def test_local_send_command_unhandled_exception_logs_error(local_api):
    """Test _send_local_command logs unhandled exceptions (lines 333-335)."""
    with aioresponses() as m:
        m.get(
            "http://192.168.1.100/get_challenge",
            body="deadbeef",
            repeat=True,
        )
        # Raise unexpected exception
        m.post(
            "http://192.168.1.100/post",
            exception=RuntimeError("Unexpected error"),
        )
        # Eventually succeed
        m.post(
            "http://192.168.1.100/post",
            status=200,
        )

        with patch.object(local_api._log, "error") as mock_error:
            await local_api._send_local_command(
                command=IntelliFireCommand.POWER, value=1
            )

            # Should log error
            assert mock_error.called


# ============================================================================
# unified_fireplace.py - Lines 126-129: perform_poll in LOCAL mode
# ============================================================================


@pytest.mark.asyncio
async def test_unified_perform_poll_local_mode():
    """Test perform_poll calls local API when in LOCAL mode (lines 126-129)."""
    mock_data = IntelliFireCommonFireplaceData(
        serial="12345",
        api_key="deadbeefdeadbeefdeadbeefdeadbeef",
        user_id="test_user",
        ip_address="192.168.1.1",
        read_mode=IntelliFireApiMode.LOCAL,
    )

    fireplace = UnifiedFireplace(fireplace_data=mock_data, use_http=True)

    # Mock the local API poll
    with patch.object(
        fireplace._local_api, "poll", new_callable=AsyncMock
    ) as mock_poll:
        await fireplace.perform_poll(timeout_seconds=5.0)

        # Should have called local API poll
        mock_poll.assert_called_once_with(timeout_seconds=5.0)


# ============================================================================
# unified_fireplace.py - Lines 126-129: perform_poll in CLOUD mode
# ============================================================================


@pytest.mark.asyncio
async def test_unified_perform_poll_cloud_mode():
    """Test perform_poll calls cloud API when not in LOCAL mode (lines 126-129)."""
    mock_data = IntelliFireCommonFireplaceData(
        serial="12345",
        api_key="deadbeefdeadbeefdeadbeefdeadbeef",
        user_id="test_user",
        ip_address="192.168.1.1",
        read_mode=IntelliFireApiMode.CLOUD,
    )

    fireplace = UnifiedFireplace(fireplace_data=mock_data, use_http=True)

    # Set read mode explicitly to CLOUD to avoid LOCAL path
    fireplace._read_mode = IntelliFireApiMode.CLOUD

    # Mock the cloud API poll
    with patch.object(
        fireplace._cloud_api, "poll", new_callable=AsyncMock
    ) as mock_poll:
        await fireplace.perform_poll(timeout_seconds=5.0)

        # Should have called cloud API poll
        mock_poll.assert_called_once_with(timeout_seconds=5.0)


# ============================================================================
# Additional edge cases for maximum coverage
# Note: Challenge failure retry is covered by test_local_send_command_challenge_failure_retry
# ============================================================================
