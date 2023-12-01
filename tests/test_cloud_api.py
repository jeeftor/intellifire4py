"""Test cloud functions."""
import pytest
from httpx import Cookies
from pytest_httpx import HTTPXMock

from intellifire4py import UnifiedFireplace
from intellifire4py.cloud_api import IntelliFireAPICloud
from intellifire4py.cloud_interface import IntelliFireCloudInterface
from intellifire4py.const import IntelliFireApiMode
from intellifire4py.exceptions import LoginError

from intellifire4py.model import IntelliFirePollData


@pytest.mark.asyncio
async def test_cloud_login(
    httpx_mock: HTTPXMock,
    enum_fireplaces_json: str,
    enum_locations_json: str,
    cloud_poll_json: str,
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

    httpx_mock.add_response(
        method="GET",
        url="https://iftapi.net/a/XXXXXE834CE109D849CBB15CDDBAFF381//apppoll",
        text=cloud_poll_json,
    )

    cloud_interface = IntelliFireCloudInterface()
    # cloud_api = IntelliFireAPICloud(serial="XXXXXE834CE109D849CBB15CDDBAFF381")
    await cloud_interface.login_with_credentials(username=username, password=password)
    user_data = cloud_interface.user_data
    fireplaces = await UnifiedFireplace.build_fireplaces_from_user_data(
        user_data,
        control_mode=IntelliFireApiMode.CLOUD,
        read_mode=IntelliFireApiMode.CLOUD,
    )

    fireplace = fireplaces[0]

    assert fireplace.serial == "XXXXXE834CE109D849CBB15CDDBAFF381"
    assert fireplace.data.brand == "H&G"
    assert fireplace.data.name == "Living Room"
    assert fireplace.api_key == api_key
    assert fireplace.data.is_on is False
    assert fireplace.data.pilot_on is True

    assert cloud_interface.user_data.user_id == user_id


@pytest.mark.asyncio
async def test_uninitialized_data() -> None:
    """Test an uninitialized data case."""
    # Create an instance of IntelliFireAPICloud
    cloud_api = IntelliFireAPICloud(serial="1234", cookies=Cookies())

    # Set _data.ipv4_address to "127.0.0.1"
    cloud_api._data.ipv4_address = "127.0.0.1"

    # Verify its uninitialized
    assert cloud_api.data == IntelliFirePollData()

    assert cloud_api.is_polling_in_background is False

    # # Test logged in
    # with pytest.raises(LoginError):
    #     await cloud_api._login_check()
    # with pytest.raises(AttributeError):
    #     cloud_api.get_fireplace_api_key()


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

    cloud_api = IntelliFireCloudInterface()
    with pytest.raises(LoginError):
        await cloud_api.login_with_credentials(username=username, password=password)


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
    cloud_poll_json: str,
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
    httpx_mock.add_response(
        method="GET",
        url="https://iftapi.net/a/XXXXXE834CE109D849CBB15CDDBAFF381//apppoll",
        text=cloud_poll_json,
    )

    cloud_api = IntelliFireCloudInterface()
    await cloud_api.login_with_credentials(username=username, password=password)
    # Fake logged in state

    # cloud_api = IntelliFireAPICloud()
    # await cloud_api.beep()  # Do nothing

    # ALl this should be mock/patched
