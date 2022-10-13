"""Test cloud functions."""
import pytest
from pytest_httpx import HTTPXMock

from intellifire4py.cloud_api import IntelliFireAPICloud


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
        url="https://iftapi.net/a//login",
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
