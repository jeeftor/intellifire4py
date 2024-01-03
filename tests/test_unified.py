"""Unified tests."""
import pytest


from intellifire4py import UnifiedFireplace
from intellifire4py.cloud_interface import IntelliFireCloudInterface
from intellifire4py.const import IntelliFireApiMode


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
        fireplaces = await UnifiedFireplace.build_fireplaces_from_user_data(
            user_data,
            control_mode=IntelliFireApiMode.NONE,
            read_mode=IntelliFireApiMode.NONE,
        )
        fireplace = fireplaces[0]

        # Double 404
        (local, cloud) = await fireplace.async_validate_connectivity()
        assert local is False
        assert cloud is False

        # 403 / Timeout
        (local, cloud) = await fireplace.async_validate_connectivity()
        assert local is False
        assert cloud is False
        (local, cloud) = await fireplace.async_validate_connectivity()
        assert local is True
        assert cloud is True
