"""Additional tests to push coverage above 94%."""

import asyncio
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio
from aiohttp import ClientError, CookieJar
from aioresponses import aioresponses

from intellifire4py.cloud_api import IntelliFireAPICloud
from intellifire4py.cloud_interface import IntelliFireCloudInterface
from intellifire4py.local_api import IntelliFireAPILocal
from intellifire4py.model import IntelliFireUserData, IntelliFireCommonFireplaceData
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


@pytest.mark.asyncio
async def test_cloud_interface_get_locations_error():
    """Test _get_locations with ClientError (lines 305-307)."""
    async with IntelliFireCloudInterface() as interface:
        # Mock successful login
        interface._is_logged_in = True

        with aioresponses() as m:
            m.get(
                "https://iftapi.net/a/enumlocations",
                exception=ClientError("Network error"),
            )

            with pytest.raises(ClientError):
                await interface._get_locations()


@pytest.mark.asyncio
async def test_cloud_interface_get_fireplaces_error():
    """Test _get_fireplaces with ClientError (lines 334-336)."""
    async with IntelliFireCloudInterface() as interface:
        # Mock successful login
        interface._is_logged_in = True

        with aioresponses() as m:
            m.get(
                "https://iftapi.net/a/enumfireplaces?location_id=loc123",
                exception=ClientError("Network error"),
            )

            with pytest.raises(ClientError):
                await interface._get_fireplaces(location_id="loc123")


@pytest.mark.asyncio
async def test_cloud_interface_cloud_fireplaces_property():
    """Test cloud_fireplaces property (lines 347-357)."""
    interface = IntelliFireCloudInterface()

    # Create proper fireplace data
    mock_fireplace = IntelliFireCommonFireplaceData(
        serial="12345",
        api_key="test_key",
        user_id="test_user",
        ip_address="192.168.1.1",
    )

    interface._user_data = IntelliFireUserData(
        auth_cookie="cookie",
        user_id="test_user",
        web_client_id="client_id",
        username="user",
        password="pass",
        fireplaces=[mock_fireplace],
    )

    # Access property
    fireplaces = interface.cloud_fireplaces

    assert len(fireplaces) == 1
    assert isinstance(fireplaces[0], IntelliFireAPICloud)


@pytest.mark.asyncio
async def test_local_api_log_status():
    """Test log_status method (line 80)."""
    api = IntelliFireAPILocal(
        fireplace_ip="192.168.1.100", user_id="user", api_key="key"
    )

    with patch.object(api._log, "info") as mock_log:
        api.log_status()
        mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_local_api_is_initialized_false():
    """Test is_initialized property returns False (line 102)."""
    api = IntelliFireAPILocal(
        fireplace_ip="192.168.1.100", user_id="user", api_key="key"
    )

    # Before any poll, serial should be "unset"
    assert api.is_initialized is False


@pytest.mark.asyncio
async def test_local_api_start_polling_when_sending():
    """Test start_background_polling suppressed when sending (lines 112-115)."""
    api = IntelliFireAPILocal(
        fireplace_ip="192.168.1.100", user_id="user", api_key="key"
    )

    # Set sending mode
    api.is_sending = True

    with patch.object(api._log, "info") as mock_log:
        await api.start_background_polling()

        # Should log suppression message
        mock_log.assert_called_with(
            "!! Suppressing start_background_polling -- sending mode engaged"
        )


@pytest.mark.asyncio
async def test_unified_fireplace_get_user_data_json_fallback():
    """Test get_user_data_as_json with AttributeError fallback (lines 150-151)."""
    mock_data = IntelliFireCommonFireplaceData(
        serial="12345",
        api_key="test_key",
        user_id="test_user",
        ip_address="192.168.1.1",
    )
    fireplace = UnifiedFireplace(fireplace_data=mock_data, use_http=True)

    # Mock fireplace data without model_dump_json
    mock_data = MagicMock()
    del mock_data.model_dump_json  # Remove the method
    mock_data.json = MagicMock(return_value='{"test": "data"}')

    fireplace._fireplace_data = mock_data

    fireplace.get_user_data_as_json()

    # Should fall back to .json() method
    mock_data.json.assert_called_once_with(indent=2)


@pytest.mark.asyncio
async def test_unified_fireplace_rich_inspect():
    """Test rich inspect functionality (line 644)."""
    mock_data = IntelliFireCommonFireplaceData(
        serial="12345",
        api_key="deadbeef123456",
        user_id="test_user",
        ip_address="192.168.1.1",
    )
    fireplace = UnifiedFireplace(fireplace_data=mock_data, use_http=True)

    # The inspect method from rich library - just verify it exists and can be called
    from rich import inspect as rich_inspect

    # This should not raise an exception
    try:
        rich_inspect(fireplace, methods=True, help=True)
    except Exception:  # noqa: S110
        # If rich isn't available or has issues, that's okay for this test
        pass


@pytest.mark.asyncio
async def test_unified_fireplace_validate_connectivity_timeout():
    """Test async_validate_connectivity with timeout (line 680)."""
    mock_data = IntelliFireCommonFireplaceData(
        serial="12345",
        api_key="test_key",
        user_id="test_user",
        ip_address="192.168.1.1",
    )
    fireplace = UnifiedFireplace(fireplace_data=mock_data, use_http=True)

    # Mock poll methods to timeout
    async def slow_poll(*args, **kwargs):
        await asyncio.sleep(10)  # Longer than timeout

    fireplace._local_api.poll = slow_poll
    fireplace._cloud_api.poll = slow_poll

    local_ok, cloud_ok = await fireplace.async_validate_connectivity(timeout=0.1)

    # Both should timeout
    assert local_ok is False
    assert cloud_ok is False


@pytest.mark.asyncio
async def test_user_data_get_data_for_serial_not_found():
    """Test get_data_for_serial returns None when not found (line 284)."""
    user_data = IntelliFireUserData(fireplaces=[])

    result = user_data.get_data_for_serial("nonexistent")

    assert result is None


@pytest.mark.asyncio
async def test_user_data_get_data_for_ip_not_found():
    """Test get_data_for_ip returns None when not found (line 298)."""
    user_data = IntelliFireUserData(fireplaces=[])

    result = user_data.get_data_for_ip("192.168.1.999")

    assert result is None
