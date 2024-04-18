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
        user_data = cloud_interface.user_data # noqa: F841



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

        with pytest.raises(ClientError) as ex:  # noqa: F841
            fp = await UnifiedFireplace.build_fireplace_from_common( # noqa: F841
                mock_common_data_local
            )
