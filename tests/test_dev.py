"""Tests for intellifire4py development utilities."""

import asyncio
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from intellifire4py.const import IntelliFireApiMode
from intellifire4py.model import IntelliFirePollData


@pytest.fixture
def mock_fp(mock_common_data_local, local_poll_json):
    """Fixture that mocks UnifiedFireplace with local poll data."""
    with patch("intellifire4py.UnifiedFireplace") as mock_unified_fireplace:
        # Create an instance of the mock
        mock_instance = mock_unified_fireplace.return_value

        # Mock methods and properties of the instance
        mock_instance.perform_cloud_poll = AsyncMock()
        mock_instance.perform_local_poll = AsyncMock()

        mock_instance.is_cloud_polling.return_value = False
        mock_instance.is_local_polling.return_value = True

        mock_instance.get_user_data_as_json.return_value = '{"mock": "data"}'

        mock_instance.ip_address = "192.168.1.100"
        mock_instance.api_key = "mock_api_key"
        mock_instance.serial = "mock_serial"
        mock_instance.user_id = "mock_user_id"
        mock_instance.auth_cookie = "mock_auth_cookie"
        mock_instance.web_client_id = "mock_web_client_id"

        mock_instance.read_api = MagicMock()  # If needed, you can mock this further
        mock_instance.control_api = MagicMock()  # If needed, you can mock this further

        mock_instance._read_mode = IntelliFireApiMode.LOCAL
        mock_instance.read_mode = IntelliFireApiMode.LOCAL

        mock_instance.control_mode = IntelliFireApiMode.LOCAL
        mock_instance._control_mode = IntelliFireApiMode.LOCAL

        # Use poll data locally
        data = IntelliFirePollData.parse_raw(local_poll_json)
        mock_instance.data = data

        mock_instance.set_read_mode = AsyncMock()
        mock_instance.set_control_mode = AsyncMock()

        mock_instance.async_validate_connectivity = AsyncMock(
            return_value=(True, False)
        )

        yield mock_instance  # Provide the mock instance to the test


def test_unified_fireplace(mock_fp):
    """Test UnifiedFireplace mock fixture."""
    # The mock_unified_fireplace fixture is automatically used in this test
    assert mock_fp.ip_address == "192.168.1.100"
    assert not mock_fp.is_cloud_polling()
    assert mock_fp.is_local_polling()

    # Call some methods and check if they were called
    asyncio.run(mock_fp.perform_cloud_poll())
    mock_fp.perform_cloud_poll.assert_called_once()

    asyncio.run(mock_fp.perform_local_poll())
    mock_fp.perform_local_poll.assert_called_once()

    assert mock_fp.data.battery == 0
    assert mock_fp.data.connection_quality == 995871
    assert mock_fp.data.downtime == 3
    assert mock_fp.data.ecm_latency == 0
    assert mock_fp.data.errors == []
    assert mock_fp.data.fanspeed == 1
    assert mock_fp.data.has_fan == 1
    assert mock_fp.data.has_light == 1
    assert mock_fp.data.has_thermostat == 1
    assert mock_fp.data.fw_ver_str == "1.3.0"
    assert mock_fp.data.fw_version == "0x01030000"
    assert mock_fp.data.flameheight == 4
    assert mock_fp.data.is_hot == 0
    assert mock_fp.data.ipv4_address == "192.168.1.69"
    assert mock_fp.data.light_level == 3
    assert mock_fp.data.name == ""
    assert mock_fp.data.pilot_on == 0
    assert mock_fp.data.is_on == 0
    assert mock_fp.data.has_power_vent == 0
    assert mock_fp.data.prepurge == 0
    assert mock_fp.data.serial == "BD0E054B5D6DF7AFBC8F9B28C9011111"
    assert mock_fp.data.raw_thermostat_setpoint == 17
    assert mock_fp.data.temperature_c == 17
    assert mock_fp.data.thermostat_on == 0
    assert mock_fp.data.timer_on == 0
    assert mock_fp.data.timeremaining_s == 0
    assert mock_fp.data.uptime == 3362
