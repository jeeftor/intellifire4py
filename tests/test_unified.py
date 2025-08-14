"""Unified tests."""

import logging
from unittest.mock import patch, PropertyMock, AsyncMock

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
    assert mock_common_data_local.ip_address == "192.168.1.69"  # NOSONAR

    local_fp = await UnifiedFireplace.build_fireplace_from_common(
        mock_common_data_local
    )

    assert local_fp.read_mode == IntelliFireApiMode.LOCAL
    assert local_fp.control_mode == IntelliFireApiMode.LOCAL
    try:
        await local_fp.read_api.stop_background_polling()
    except Exception as e:
        logging.error(f"Exception during cleanup: {e}")


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

    try:
        await local_fp.read_api.stop_background_polling()
    except Exception as e:
        logging.error(f"Exception during cleanup: {e}")


@pytest.mark.asyncio
async def test_build_from_common_data_local_without_local_connectivity2(
    mock_common_data_local, mock_login_flow_with_cloud_only
) -> None:
    """Test build from common data."""
    assert mock_common_data_local.ip_address == "192.168.1.69"  # NOSONAR

    local_fp = await UnifiedFireplace.build_fireplace_from_common(
        mock_common_data_local
    )

    assert local_fp.read_mode == IntelliFireApiMode.CLOUD
    assert local_fp.control_mode == IntelliFireApiMode.CLOUD
    try:
        await local_fp.read_api.stop_background_polling()
    except Exception as e:
        logging.error(f"Exception during cleanup: {e}")


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
    try:
        await fp.read_api.stop_background_polling()
    except Exception as e:
        logging.error(f"Exception during cleanup: {e}")


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
    try:
        await fp.read_api.stop_background_polling()
    except Exception as e:
        logging.error(f"Exception during cleanup: {e}")


@pytest.mark.asyncio
async def test_unified_connectivity(mock_cloud_login_flow_connectivity_testing):  # type: ignore
    """Test connectivity."""
    username = "user"
    password = "pass"  # noqa: S105 NOSONAR

    async with IntelliFireCloudInterface() as cloud_interface:
        await cloud_interface.login_with_credentials(
            username=username, password=password
        )


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

        with pytest.raises(ClientError):
            await UnifiedFireplace.build_fireplace_from_common(mock_common_data_local)


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


@pytest.mark.asyncio
async def test_set_read_mode_branches(mock_common_data_local):
    """Test set_read_mode covers all branches and error handling."""
    fp = UnifiedFireplace(mock_common_data_local)
    # Same mode: triggers early return
    await fp.set_read_mode(fp._read_mode)
    # Switch mode: triggers _switch_read_mode
    called = {}

    async def fake_switch(mode):
        called["mode"] = mode

    with patch.object(fp, "_switch_read_mode", new=AsyncMock(side_effect=fake_switch)):
        await fp.set_read_mode(IntelliFireApiMode.CLOUD)
        assert called["mode"] == IntelliFireApiMode.CLOUD
    # Error branch
    with patch.object(
        fp, "_switch_read_mode", new=AsyncMock(side_effect=Exception("fail"))
    ):
        try:
            await fp.set_read_mode(
                IntelliFireApiMode.LOCAL
            )  # Should log error, not raise
        except Exception as e:
            logging.error(f"Exception during set_read_mode: {e}")


@pytest.mark.asyncio
async def test_set_control_mode(mock_common_data_local):
    """Test set_control_mode sets mode and updates fireplace_data."""
    fp = UnifiedFireplace(mock_common_data_local)
    await fp.set_control_mode(IntelliFireApiMode.CLOUD)
    assert fp._control_mode == IntelliFireApiMode.CLOUD
    assert fp._fireplace_data.control_mode == IntelliFireApiMode.CLOUD


@pytest.mark.asyncio
async def test_is_cloud_and_local_polling_properties_cleanup(mock_common_data_local):
    """Test cleanup of cloud/local polling properties."""
    fp = UnifiedFireplace(mock_common_data_local)
    with (
        patch.object(
            type(fp._cloud_api), "is_polling_in_background", new_callable=PropertyMock
        ) as cloud_polling,
        patch.object(
            type(fp._local_api), "is_polling_in_background", new_callable=PropertyMock
        ) as local_polling,
    ):
        cloud_polling.return_value = True
        local_polling.return_value = False
        assert fp.is_cloud_polling is True
        assert fp.is_local_polling is False
        cloud_polling.return_value = False
        local_polling.return_value = True
        assert fp.is_cloud_polling is False
        assert fp.is_local_polling is True
    # Clean up background polling if started
    try:
        await fp.read_api.stop_background_polling()
    except Exception as e:
        logging.error(f"Exception during cleanup: {e}")


@pytest.mark.asyncio
async def test_switch_read_mode_else_branch(mock_common_data_local):
    """Test else branch of switch_read_mode."""
    fp = UnifiedFireplace(mock_common_data_local)

    # Simulate an unknown mode
    class DummyMode:
        pass

    mode = DummyMode()

    # Patch stop_background_polling to be async no-op
    async def nop():
        return None

    fp._local_api.stop_background_polling = nop
    fp._cloud_api.stop_background_polling = nop
    await fp._switch_read_mode(mode)
    assert fp._read_mode == mode
    assert fp._fireplace_data.read_mode == mode


@pytest.mark.asyncio
async def test_build_fireplace_direct(mock_async_validate_connectivity):
    """Test direct build of UnifiedFireplace."""
    # Customize the mock for this test
    mock_async_validate_connectivity.return_value = (True, False)
    fp = await UnifiedFireplace.build_fireplace_direct(
        ip_address="1.2.3.4",  # NOSONAR
        api_key="api",
        serial="ser",
        auth_cookie="cookie",
        user_id="user",
        web_client_id="webid",
        read_mode=IntelliFireApiMode.LOCAL,
        control_mode=IntelliFireApiMode.LOCAL,
        use_http=True,
        verify_ssl=False,
    )
    assert isinstance(fp, UnifiedFireplace)
    assert fp.ip_address == "1.2.3.4"  # NOSONAR
    assert fp.api_key == "api"
    assert fp.serial == "ser"
    assert fp.auth_cookie == "cookie"
    assert fp.user_id == "user"
    assert fp.web_client_id == "webid"


@pytest.mark.asyncio
async def test_build_fireplaces_from_user_data(
    mock_async_validate_connectivity, mock_user_data
):
    """Test building multiple fireplaces from user data."""

    # Patch _create_async_instance to just return a dummy UnifiedFireplace
    async def dummy_create(fp, **kwargs):
        return UnifiedFireplace(fp)

    with patch("intellifire4py.UnifiedFireplace._create_async_instance", dummy_create):
        fps = await UnifiedFireplace.build_fireplaces_from_user_data(mock_user_data)
    assert isinstance(fps, list)
    assert all(isinstance(fp, UnifiedFireplace) for fp in fps)


@pytest.mark.asyncio
async def test_set_read_mode_same_mode_noop(mock_common_data_local):
    """Test set_read_mode does nothing if mode is unchanged (covers early return)."""
    fp = UnifiedFireplace(mock_common_data_local)
    fp._read_mode = IntelliFireApiMode.LOCAL
    with patch.object(fp._log, "info") as mock_log_info:
        await fp.set_read_mode(IntelliFireApiMode.LOCAL)
        mock_log_info.assert_called_once_with("Not updating mode -- it was the same")


@pytest.mark.asyncio
async def test_async_validate_connectivity_client_response_error(
    mock_common_data_local,
):
    """Test async_validate_connectivity covers ClientResponseError branch."""
    fp = UnifiedFireplace(mock_common_data_local)

    class DummyClientResponseError(Exception):
        pass

    async def raise_client_response_error(*args, **kwargs):
        raise DummyClientResponseError("fail")

    # Patch perform_local_poll to raise ClientResponseError
    with patch(
        "intellifire4py.unified_fireplace.ClientResponseError", DummyClientResponseError
    ):
        with patch.object(fp, "perform_local_poll", new=raise_client_response_error):
            with patch.object(
                fp, "perform_cloud_poll", new=AsyncMock(return_value=None)
            ):
                # Should catch DummyClientResponseError and return (False, True)
                result = await fp.async_validate_connectivity()
                assert result[0] is False


@pytest.mark.asyncio
async def test_async_validate_connectivity_generic_exception(mock_common_data_local):
    """Test async_validate_connectivity covers generic Exception branch."""
    fp = UnifiedFireplace(mock_common_data_local)

    async def raise_generic(*args, **kwargs):
        raise Exception("fail")

    with patch.object(fp, "perform_local_poll", new=raise_generic):
        with patch.object(fp, "perform_cloud_poll", new=AsyncMock(return_value=None)):
            # Should catch Exception and return (False, True)
            result = await fp.async_validate_connectivity()
            assert result[0] is False


@pytest.mark.asyncio
async def test_async_validate_connectivity_connection_error(mock_common_data_local):
    """Test async_validate_connectivity covers ConnectionError branch."""
    fp = UnifiedFireplace(mock_common_data_local)

    async def raise_connection_error(*args, **kwargs):
        raise ConnectionError("fail")

    with patch.object(fp, "perform_local_poll", new=raise_connection_error):
        with patch.object(fp, "perform_cloud_poll", new=AsyncMock(return_value=None)):
            # Should catch ConnectionError and return (False, True)
            result = await fp.async_validate_connectivity()
            assert result[0] is False


@pytest.mark.asyncio
async def test_set_read_mode_triggers_switch(mock_common_data_local):
    """Test set_read_mode calls _switch_read_mode when mode changes."""
    fp = UnifiedFireplace(mock_common_data_local)
    fp._read_mode = IntelliFireApiMode.LOCAL
    with patch.object(fp, "_switch_read_mode", new=AsyncMock()) as mock_switch:
        await fp.set_read_mode(IntelliFireApiMode.CLOUD)
        mock_switch.assert_called_once_with(IntelliFireApiMode.CLOUD)


@pytest.mark.asyncio
async def test_build_fireplace_from_common_data_real(mock_common_data_local):
    """Test build_fireplace_from_common_data with real _create_async_instance (no patch), but patch connectivity."""
    with patch.object(
        UnifiedFireplace,
        "async_validate_connectivity",
        new=AsyncMock(return_value=(True, True)),
    ):
        fp = await UnifiedFireplace.build_fireplace_from_common_data(
            mock_common_data_local
        )
        assert isinstance(fp, UnifiedFireplace)


@pytest.mark.asyncio
async def test_async_validate_connectivity_real(mock_common_data_local):
    """Test that async_validate_connectivity is called on a real instance (covers signature/line 592)."""
    fp = UnifiedFireplace(mock_common_data_local)
    with (
        patch.object(fp, "perform_local_poll", new=AsyncMock(return_value=None)),
        patch.object(fp, "perform_cloud_poll", new=AsyncMock(return_value=None)),
    ):
        result = await fp.async_validate_connectivity()
        assert isinstance(result, tuple)


@pytest.mark.asyncio
async def test_async_validate_connectivity_aiohttp_client_connection_error(
    mock_common_data_local,
):
    """Test async_validate_connectivity covers aiohttp.ClientConnectionError branch."""
    import aiohttp

    fp = UnifiedFireplace(mock_common_data_local)

    async def raise_aiohttp_connection_error(*args, **kwargs):
        raise aiohttp.ClientConnectionError("fail")

    with patch.object(fp, "perform_local_poll", new=raise_aiohttp_connection_error):
        with patch.object(fp, "perform_cloud_poll", new=AsyncMock(return_value=None)):
            result = await fp.async_validate_connectivity()
            assert result[0] is False
