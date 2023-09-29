"""Test cloud functions."""
import pytest
from pytest_httpx import HTTPXMock

from intellifire4py.cloud_api import IntelliFireAPICloud
from intellifire4py.exceptions import LoginError

from intellifire4py.model import IntelliFirePollData, IntelliFireFireplace


@pytest.mark.asyncio
async def test_cloud_login(
    httpx_mock: HTTPXMock,
    enum_fireplaces_json: str,
    enum_locations_json: str,
    cookies: list[tuple[str, str]],
    user_id: str,
    api_key: str,
) -> None:
    """Test cloud login."""
    username = "user"
    password = "pass"  # noqa: S105
    httpx_mock.add_response(
        method="POST",
        url="https://iftapi.net/a/login",
        status_code=204,
        headers=cookies,
    )
    httpx_mock.add_response(
        method="GET",
        url="https://iftapi.net/a/enumlocations",
        text=enum_locations_json,
    )

    httpx_mock.add_response(
        method="GET",
        url="https://iftapi.net/a/enumfireplaces?location_id=11118333339267293392",
        text=enum_fireplaces_json,
    )

    cloud_api = IntelliFireAPICloud()
    await cloud_api.login(username=username, password=password)

    assert cloud_api.default_fireplace.serial == "XXXXXE834CE109D849CBB15CDDBAFF381"
    assert cloud_api.default_fireplace.brand == "H&G"
    assert cloud_api.default_fireplace.name == "Living Room"
    assert cloud_api.default_fireplace.apikey == api_key
    assert cloud_api.default_fireplace.power == "0"
    assert cloud_api.get_user_id() == user_id
    assert cloud_api.get_fireplace_api_key() == "12345BDB2D97B3DC7CEE8A8B05DD5FFA"

    fireplace_dict = {
        "serial": "12345",
        "brand": "BrandX",
        "name": "Living Room",
        "apikey": "abc123",
        "power": "on",
    }
    assert (
        cloud_api.get_fireplace_api_key(IntelliFireFireplace(**fireplace_dict))
        == "abc123"
    )


@pytest.mark.asyncio
async def test_uninitialized_data() -> None:
    """Test an uninitialized data case."""
    # Create an instance of IntelliFireAPICloud
    cloud_api = IntelliFireAPICloud()

    # Set _data.ipv4_address to "127.0.0.1"
    cloud_api._data.ipv4_address = "127.0.0.1"

    # Verify its uninitialized
    assert cloud_api.data == IntelliFirePollData()

    assert cloud_api.is_polling_in_background is False

    # Test logged in
    with pytest.raises(LoginError):
        await cloud_api._login_check()
    with pytest.raises(AttributeError):
        cloud_api.get_fireplace_api_key()


@pytest.mark.asyncio
async def test_incorrect_login_credentials(httpx_mock: HTTPXMock) -> None:
    """Test login with incorrect credentials."""
    username = "incorrect_user"
    password = "incorrect_password"  # noqa S105
    httpx_mock.add_response(
        method="POST",
        url="https://iftapi.net/a/login",
        status_code=403,  # Simulating incorrect credentials
    )

    cloud_api = IntelliFireAPICloud()
    with pytest.raises(LoginError):
        await cloud_api.login(username=username, password=password)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status_code, expected_error",
    [
        (204, None),  # Success
        (403, "Not authorized"),
        (404, "Fireplace not found (bad serial number)"),
        (422, "Invalid Parameter (invalid command id or command value)"),
        (69, "Unexpected return code"),
    ],
)
async def test_sending(
    httpx_mock: HTTPXMock,
    status_code: int,
    expected_error: str,
    enum_fireplaces_json: str,
    enum_locations_json: str,
    cookies: list[tuple[str, str]],
    user_id: str,
    api_key: str,
) -> None:
    """Test some sending."""
    username = "user"
    password = "pass"  # noqa: S105
    httpx_mock.add_response(
        method="POST",
        url="https://iftapi.net/a/login",
        status_code=204,
        headers=cookies,
    )
    httpx_mock.add_response(
        method="GET",
        url="https://iftapi.net/a/enumlocations",
        text=enum_locations_json,
    )

    httpx_mock.add_response(
        method="GET",
        url="https://iftapi.net/a/enumfireplaces?location_id=11118333339267293392",
        text=enum_fireplaces_json,
    )

    cloud_api = IntelliFireAPICloud()
    await cloud_api.login(username=username, password=password)
    # Fake logged in state

    cloud_api = IntelliFireAPICloud()
    await cloud_api.beep()  # Do nothing

    # ALl this should be mock/patched
