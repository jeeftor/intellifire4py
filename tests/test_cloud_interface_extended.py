"""Extended tests for cloud_interface.py to improve coverage."""

import pytest
from aiohttp import ClientError
from aioresponses import aioresponses

from intellifire4py.cloud_interface import IntelliFireCloudInterface
from intellifire4py.exceptions import LoginError


@pytest.mark.asyncio
async def test_login_with_credentials_aiohttp_error():
    """Test login_with_credentials handles aiohttp.ClientError."""
    async with IntelliFireCloudInterface() as cloud_interface:
        with aioresponses() as m:
            m.post(
                "https://iftapi.net/a/login",
                exception=ClientError("Network error"),
            )

            with pytest.raises(ClientError):
                await cloud_interface.login_with_credentials(
                    username="user", password="pass"
                )


@pytest.mark.asyncio
async def test_login_check_not_logged_in():
    """Test _login_check raises LoginError when not logged in."""
    async with IntelliFireCloudInterface() as cloud_interface:
        with pytest.raises(LoginError, match="Not Logged In"):
            await cloud_interface._login_check()


@pytest.mark.asyncio
async def test_get_locations_not_logged_in():
    """Test _get_locations raises LoginError when not logged in."""
    async with IntelliFireCloudInterface() as cloud_interface:
        with pytest.raises(LoginError, match="Not Logged In"):
            await cloud_interface._get_locations()


@pytest.mark.asyncio
async def test_get_fireplaces_not_logged_in():
    """Test _get_fireplaces raises LoginError when not logged in."""
    async with IntelliFireCloudInterface() as cloud_interface:
        with pytest.raises(LoginError, match="Not Logged In"):
            await cloud_interface._get_fireplaces(location_id="test_location")


def test_load_user_data():
    """Test load_user_data parses JSON correctly."""
    json_str = '{"username": "test", "password": "test", "auth_cookie": "cookie", "user_id": "123", "web_client_id": "456", "fireplaces": []}'

    cloud_interface = IntelliFireCloudInterface()
    user_data = cloud_interface.load_user_data(json_str)

    assert user_data.username == "test"
    assert user_data.user_id == "123"
    assert user_data.web_client_id == "456"


@pytest.mark.asyncio
async def test_context_manager_usage():
    """Test that methods require async context manager."""
    cloud_interface = IntelliFireCloudInterface()

    with pytest.raises(RuntimeError, match="must be called within an 'async with' context"):
        await cloud_interface.login_with_credentials(
            username="user", password="pass"
        )
