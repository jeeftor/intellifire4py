"""Shared config file."""
import asyncio
import os

import pytest
from aioresponses import aioresponses


@pytest.fixture
def local_poll_json() -> str:
    """Define a fixture to hold response data."""
    return open(f"{os.path.dirname(__file__)}/fixtures/poll.json").read()


@pytest.fixture
def poll_response_text_error_6_642() -> str:
    """Define a fixture to hold response data."""
    return open(f"{os.path.dirname(__file__)}/fixtures/error_6_642.json").read()


@pytest.fixture
def enum_locations_json() -> str:
    """Define a fixture to hold response data."""
    return open(f"{os.path.dirname(__file__)}/fixtures/enumlocations.json").read()


@pytest.fixture
def enum_fireplaces_json() -> str:
    """Define a fixture to hold response data."""
    return open(f"{os.path.dirname(__file__)}/fixtures/enumfireplaces.json").read()


@pytest.fixture
def cloud_poll_json() -> str:
    """Define a fixture to hold response data."""
    return open(f"{os.path.dirname(__file__)}/fixtures/cloud_poll.json").read()


@pytest.fixture
def user_id() -> str:
    """Return mock user id."""
    return "XXXXE5DA5C74BD88ED1BC00716791092DE495232B69B4631CD79F90ADC10580E"


@pytest.fixture
def api_key() -> str:
    """Mock api key."""
    return "12345BDB2D97B3DC7CEE8A8B05DD5FFA"


@pytest.fixture
def challenge_text() -> str:
    """Mock challenge text."""
    return "82FC7D369EC9B59B1A054ADE85F2AF76"


@pytest.fixture
def cookies(user_id: str) -> list[tuple[str, str]]:
    """Mock cookies."""
    return [
        ("set-cookie", "auth_cookie=XXXX1B56D18B52DC8F94DC0E5DC89A90"),
        (
            "set-cookie",
            f"user={user_id}",
        ),
        ("set-cookie", "web_client_id=XXXX21C9A75384EA726071BFCC95E3F6"),
    ]


@pytest.fixture
def mock_aioresponse():
    with aioresponses() as m:
        yield m


@pytest.fixture
def mock_cloud_login_flow(
    cookies,
    enum_locations_json: str,
    enum_fireplaces_json: str,
    cloud_poll_json: str,
    local_poll_json,
):
    with aioresponses() as m:
        # Mock the POST login request
        m.post("https://iftapi.net/a/login", status=204, headers=cookies)

        # Mock the GET enumlocations request
        m.get(
            "https://iftapi.net/a/enumlocations", status=200, body=enum_locations_json
        )

        m.get(
            "https://iftapi.net/a/enumfireplaces?location_id=11118333339267293392",
            status=200,
            body=enum_fireplaces_json,
        )
        m.get(
            "https://iftapi.net/a/XXXXXE834CE109D849CBB15CDDBAFF381//apppoll",
            status=200,
            body=cloud_poll_json,
            repeat=True,
        )
        yield m


@pytest.fixture
def mock_cloud_login_flow_connectivity_testing(
    cookies,
    enum_locations_json: str,
    enum_fireplaces_json: str,
    cloud_poll_json: str,
    local_poll_json,
):
    with aioresponses() as m:
        # Mock the POST login request
        m.post("https://iftapi.net/a/login", status=204, headers=cookies)

        # Mock the GET enumlocations request
        m.get(
            "https://iftapi.net/a/enumlocations", status=200, body=enum_locations_json
        )

        m.get(
            "https://iftapi.net/a/enumfireplaces?location_id=11118333339267293392",
            status=200,
            body=enum_fireplaces_json,
        )
        m.get(
            "https://iftapi.net/a/XXXXXE834CE109D849CBB15CDDBAFF381//apppoll",
            status=200,
            body=cloud_poll_json,
            repeat=False,
        )

        # Double 404
        m.get(
            "https://iftapi.net/a/XXXXXE834CE109D849CBB15CDDBAFF381//apppoll",
            status=404,
            # body=cloud_poll_json,
            # repeat=False,
        )
        m.get(
            url="http://192.168.1.69/poll",
            status=404,
        )

        # 403 / timeout
        m.get(
            "https://iftapi.net/a/XXXXXE834CE109D849CBB15CDDBAFF381//apppoll",
            status=403,  # bad credentials
        )
        m.get(
            url="http://192.168.1.69/poll",
            body=None,
            exception=asyncio.TimeoutError(),
        )

        # All is finally good
        m.get(
            "https://iftapi.net/a/XXXXXE834CE109D849CBB15CDDBAFF381//apppoll",
            status=200,
            body=cloud_poll_json,
            repeat=False,
        )
        m.get(
            url="http://192.168.1.69/poll",
            status=200,
            body=local_poll_json,
        )
        yield m


#
# @pytest.fixture
# def mock_local_poll(local_poll_json):
#     with aioresponses() as m:
#         m.get(f"http://192.168.1.69/poll", status=200, body=local_poll_json)
#         m.post(f"http://192.168.1.69/post", status=200, repeat=True)
#
#         yield m


@pytest.fixture
def mock_login_bad_credentials():
    with aioresponses() as m:
        m.post("https://iftapi.net/a/login", status=403)
        yield m
