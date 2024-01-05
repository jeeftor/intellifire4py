"""Unified tests."""
import pytest


from intellifire4py import UnifiedFireplace
from intellifire4py.cloud_interface import IntelliFireCloudInterface
from intellifire4py.const import IntelliFireApiMode
from intellifire4py.model import IntelliFireCommonFireplaceData


@pytest.mark.asyncio
async def test_build_from_common_data(mock_login_for_unified_test):
    """Test unified firepalce construction control/read mode issues."""
    common_data_local = IntelliFireCommonFireplaceData(
        auth_cookie="cookie",
        user_id="user",
        web_client_id="id",
        serial="XXXXXE834CE109D849CBB15CDDBAFF381",
        api_key="api_key",
        ip_address="192.168.1.69",
        read_mode=IntelliFireApiMode.LOCAL,
        control_mode=IntelliFireApiMode.LOCAL,
    )

    common_data_cloud = IntelliFireCommonFireplaceData(
        auth_cookie="cookie",
        user_id="user",
        web_client_id="id",
        serial="XXXXXE834CE109D849CBB15CDDBAFF381",
        api_key="api_key",
        ip_address="192.168.1.69",
        read_mode=IntelliFireApiMode.CLOUD,
        control_mode=IntelliFireApiMode.CLOUD,
    )

    common_data_none = IntelliFireCommonFireplaceData(
        auth_cookie="cookie",
        user_id="user",
        web_client_id="id",
        serial="XXXXXE834CE109D849CBB15CDDBAFF381",
        api_key="api_key",
        ip_address="192.168.1.69",
        read_mode=IntelliFireApiMode.NONE,
        control_mode=IntelliFireApiMode.NONE,
    )

    local_fp = await UnifiedFireplace.build_fireplace_from_common(common_data_local)
    cloud_fp = await UnifiedFireplace.build_fireplace_from_common(common_data_cloud)
    none_fp = await UnifiedFireplace.build_fireplace_from_common(common_data_none)

    assert local_fp.read_mode == IntelliFireApiMode.LOCAL
    assert local_fp.control_mode == IntelliFireApiMode.LOCAL

    assert cloud_fp.read_mode == IntelliFireApiMode.CLOUD
    assert cloud_fp.control_mode == IntelliFireApiMode.CLOUD
    assert cloud_fp.read_mode == IntelliFireApiMode.CLOUD
    assert cloud_fp.control_mode == IntelliFireApiMode.CLOUD

    assert none_fp.read_mode == IntelliFireApiMode.NONE
    assert none_fp.control_mode == IntelliFireApiMode.NONE


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

        assert user_data.get_data_for_ip(
            fireplace.ip_address
        ) == user_data.get_data_for_serial(fireplace.serial)

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
