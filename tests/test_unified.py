"""Unified tests."""
from unittest.mock import patch

import pytest

from aiohttp import ClientError

from intellifire4py import UnifiedFireplace
from intellifire4py.cloud_interface import IntelliFireCloudInterface
from intellifire4py.const import IntelliFireApiMode


@pytest.mark.asyncio
async def test_build_from_common_data_local_with_local_connectivity(
    mock_common_data_local, mock_login_flow_with_local_and_cloud
) -> None:
    """Test build from common data."""
    assert mock_common_data_local.ip_address == "192.168.1.69"

    local_fp = await UnifiedFireplace.build_fireplace_from_common(
        mock_common_data_local
    )

    assert local_fp.read_mode == IntelliFireApiMode.LOCAL
    assert local_fp.control_mode == IntelliFireApiMode.LOCAL
    await local_fp.read_api.stop_background_polling()


@pytest.mark.asyncio
async def test_build_from_common_data_local_with_local_connectivity1(
    mock_common_data_cloud, mock_login_flow_with_local_and_cloud
) -> None:
    """Test build from common data."""
    local_fp = await UnifiedFireplace.build_fireplace_from_common(
        mock_common_data_cloud
    )

    assert local_fp.read_mode == IntelliFireApiMode.CLOUD
    assert local_fp.control_mode == IntelliFireApiMode.CLOUD

    await local_fp.read_api.stop_background_polling()


@pytest.mark.asyncio
async def test_build_from_common_data_local_without_local_connectivity2(
    mock_common_data_local, mock_login_flow_with_cloud_only
) -> None:
    """Test build from common data."""
    assert mock_common_data_local.ip_address == "192.168.1.69"

    local_fp = await UnifiedFireplace.build_fireplace_from_common(
        mock_common_data_local
    )

    assert local_fp.read_mode == IntelliFireApiMode.CLOUD
    assert local_fp.control_mode == IntelliFireApiMode.CLOUD
    await local_fp.read_api.stop_background_polling()


@pytest.mark.asyncio
async def test_build_with_user_data_cloud_only(
    mock_user_data, mock_cloud_login_flow_no_local
):
    """Test build with user data."""
    fp = (
        await UnifiedFireplace.build_fireplaces_from_user_data(user_data=mock_user_data)
    )[0]

    assert fp.read_mode == IntelliFireApiMode.CLOUD
    assert fp.control_mode == IntelliFireApiMode.CLOUD

    assert fp.cloud_connectivity is True
    assert fp.local_connectivity is False
    await fp.read_api.stop_background_polling()


@pytest.mark.asyncio
async def test_build_with_user_data_cloud_and_local(
    mock_user_data, mock_login_flow_with_local_and_cloud
):
    """Test build with user data."""
    fp = (
        await UnifiedFireplace.build_fireplaces_from_user_data(user_data=mock_user_data)
    )[0]

    assert fp.read_mode == IntelliFireApiMode.LOCAL
    assert fp.control_mode == IntelliFireApiMode.LOCAL

    assert fp.cloud_connectivity is True
    assert fp.local_connectivity is True
    await fp.read_api.stop_background_polling()


@pytest.mark.asyncio
async def test_unified_connectivity(mock_cloud_login_flow_connectivity_testing):  # type: ignore
    """Test connectivity."""
    username = "user"
    password = "pass"  # noqa: S105

    async with IntelliFireCloudInterface() as cloud_interface:
        await cloud_interface.login_with_credentials(
            username=username, password=password
        )
        user_data = cloud_interface.user_data


@pytest.mark.asyncio
async def test_connectivity_cloud_only(mock_common_data_local, mock_background_polling):
    """Test connectivity."""
    with patch("intellifire4py.UnifiedFireplace.async_validate_connectivity") as m:
        m.return_value = (False, True)

        fp = await UnifiedFireplace.build_fireplace_from_common(mock_common_data_local)

        assert fp.local_connectivity is False
        assert fp.cloud_connectivity is True


@pytest.mark.asyncio
async def test_connectivity_local_only(mock_common_data_local, mock_background_polling):
    """Test connectivity."""
    with patch("intellifire4py.UnifiedFireplace.async_validate_connectivity") as m:
        m.return_value = (True, False)

        fp = await UnifiedFireplace.build_fireplace_from_common(mock_common_data_local)

        assert fp.local_connectivity is True
        assert fp.cloud_connectivity is False


@pytest.mark.asyncio
async def test_connectivity_none(mock_common_data_local, mock_background_polling):
    """Test connectivity."""
    with patch("intellifire4py.UnifiedFireplace.async_validate_connectivity") as m:
        m.return_value = (False, False)

        with pytest.raises(ClientError) as ex:
            fp = await UnifiedFireplace.build_fireplace_from_common(
                mock_common_data_local
            )


@pytest.mark.asyncio
async def test_property_access(mock_common_data_local):
    """Test property accessors for UnifiedFireplace."""
    fp = UnifiedFireplace(mock_common_data_local)
    assert fp.ip_address == mock_common_data_local.ip_address
    assert fp.api_key == mock_common_data_local.api_key
    assert fp.serial == mock_common_data_local.serial
    assert fp.user_id == mock_common_data_local.user_id
    assert fp.auth_cookie == mock_common_data_local.auth_cookie
    assert fp.web_client_id == mock_common_data_local.web_client_id
    json_str = fp.get_user_data_as_json()
    assert isinstance(json_str, str)


@pytest.mark.asyncio
async def test_read_and_control_api_switch(mock_common_data_local):
    """Test read_api and control_api switching logic."""
    fp = UnifiedFireplace(mock_common_data_local)
    fp._read_mode = IntelliFireApiMode.LOCAL
    assert fp.read_api is fp._local_api
    fp._read_mode = IntelliFireApiMode.CLOUD
    assert fp.read_api is fp._cloud_api
    fp._control_mode = IntelliFireApiMode.LOCAL
    assert fp.control_api is fp._local_api
    fp._control_mode = IntelliFireApiMode.CLOUD
    assert fp.control_api is fp._cloud_api


@pytest.mark.asyncio
async def test_data_property(mock_common_data_local):
    """Test data property returns correct data based on mode."""
    fp = UnifiedFireplace(mock_common_data_local)
    fp._read_mode = IntelliFireApiMode.LOCAL
    assert fp.data == fp._local_api.data
    fp._read_mode = IntelliFireApiMode.CLOUD
    assert fp.data == fp._cloud_api.data


import pytest
@pytest.mark.asyncio
async def test_set_read_mode_branches(monkeypatch, mock_common_data_local):
    """Test set_read_mode covers all branches and error handling."""
    fp = UnifiedFireplace(mock_common_data_local)
    # Same mode: triggers early return
    await fp.set_read_mode(fp._read_mode)
    # Switch mode: triggers _switch_read_mode
    called = {}
    async def fake_switch(mode):
        called['mode'] = mode
    fp._switch_read_mode = fake_switch
    await fp.set_read_mode(IntelliFireApiMode.CLOUD)
    assert called['mode'] == IntelliFireApiMode.CLOUD
    # Error branch
    async def raise_exc(mode):
        raise Exception("fail")
    fp._switch_read_mode = raise_exc
    await fp.set_read_mode(IntelliFireApiMode.LOCAL)  # Should log error, not raise

@pytest.mark.asyncio
async def test_set_control_mode(mock_common_data_local):
    """Test set_control_mode sets mode and updates fireplace_data."""
    fp = UnifiedFireplace(mock_common_data_local)
    await fp.set_control_mode(IntelliFireApiMode.CLOUD)
    assert fp._control_mode == IntelliFireApiMode.CLOUD
    assert fp._fireplace_data.control_mode == IntelliFireApiMode.CLOUD
