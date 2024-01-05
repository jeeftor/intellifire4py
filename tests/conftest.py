"""Shared config file."""

import asyncio
import os
from collections.abc import Generator
import pytest
from aioresponses import aioresponses

# Define fixtures for various test scenarios.


@pytest.fixture
def local_poll_json() -> str:
    """Define a fixture to hold response data."""
    # Reads and returns the content of local_poll.json
    return open(f"{os.path.dirname(__file__)}/fixtures/local_poll.json").read()


@pytest.fixture
def poll_response_text_error_6_642() -> str:
    """Define a fixture to hold response data."""
    # Reads and returns the content of error_6_642.json
    return open(f"{os.path.dirname(__file__)}/fixtures/error_6_642.json").read()


@pytest.fixture
def enum_locations_json() -> str:
    """Define a fixture to hold response data."""
    # Reads and returns the content of enumlocations.json
    return open(f"{os.path.dirname(__file__)}/fixtures/enumlocations.json").read()


@pytest.fixture
def enum_fireplaces_json() -> str:
    """Define a fixture to hold response data."""
    # Reads and returns the content of enumfireplaces.json
    return open(f"{os.path.dirname(__file__)}/fixtures/enumfireplaces.json").read()


@pytest.fixture
def cloud_poll_json() -> str:
    """Define a fixture to hold response data."""
    # Reads and returns the content of cloud_poll.json
    return open(f"{os.path.dirname(__file__)}/fixtures/cloud_poll.json").read()


@pytest.fixture
def user_id() -> str:
    """Return mock user id."""
    # Returns a mock user ID
    return "XXXXE5DA5C74BD88ED1BC00716791092DE495232B69B4631CD79F90ADC10580E"


@pytest.fixture
def api_key() -> str:
    """Mock api key."""
    # Returns a mock API key
    return "12345BDB2D97B3DC7CEE8A8B05DD5FFA"


@pytest.fixture
def challenge_text() -> str:
    """Mock challenge text."""
    # Returns a mock challenge text
    return "82FC7D369EC9B59B1A054ADE85F2AF76"


@pytest.fixture
def cookies(user_id: str) -> list[tuple[str, str]]:
    """Mock cookies."""
    # Returns a list of mock cookies
    return [
        ("set-cookie", "auth_cookie=XXXX1B56D18B52DC8F94DC0E5DC89A90"),
        ("set-cookie", f"user={user_id}"),
        ("set-cookie", "web_client_id=XXXX21C9A75384EA726071BFCC95E3F6"),
    ]


@pytest.fixture
def mock_aioresponse() -> Generator[aioresponses, None, None]:
    """Mock out an aioresponse but i'm not sure if we even use this."""
    # Context manager for mocking aiohttp responses
    with aioresponses() as m:
        yield m


def setup_common_mocks(
    m: aioresponses,
    cookies: list[tuple[str, str]],
    enum_locations_json: str,
    enum_fireplaces_json: str,
    cloud_poll_json: str,
    repeat: bool = False,
) -> None:
    """Sets up common mocks for HTTP requests."""
    # Mock the POST login request
    m.post("https://iftapi.net/a/login", status=204, headers=cookies)

    # Mock the GET enumlocations request
    m.get("https://iftapi.net/a/enumlocations", status=200, body=enum_locations_json)

    # Mock additional HTTP requests as needed
    m.get(
        "https://iftapi.net/a/enumfireplaces?location_id=11118333339267293392",
        status=200,
        body=enum_fireplaces_json,
    )
    m.get(
        "https://iftapi.net/a/XXXXXE834CE109D849CBB15CDDBAFF381//apppoll",
        status=200,
        body=cloud_poll_json,
        repeat=repeat,
    )


@pytest.fixture
def mock_cloud_login_flow(
    cookies: list[tuple[str, str]],
    enum_locations_json: str,
    enum_fireplaces_json: str,
    cloud_poll_json: str,
    local_poll_json: str,
) -> Generator[aioresponses, None, None]:
    """Mock the login flow."""
    with aioresponses() as m:
        setup_common_mocks(
            m,
            cookies,
            enum_locations_json,
            enum_fireplaces_json,
            cloud_poll_json,
            repeat=True,
        )
        yield m


@pytest.fixture
def mock_login_for_unified_test(
    cookies: list[tuple[str, str]],
    enum_locations_json: str,
    enum_fireplaces_json: str,
    cloud_poll_json: str,
    local_poll_json: str,
) -> Generator[aioresponses, None, None]:
    """Mock the login flow."""
    with aioresponses() as m:
        setup_common_mocks(
            m,
            cookies,
            enum_locations_json,
            enum_fireplaces_json,
            cloud_poll_json,
            repeat=True,
        )
        m.get(url="http://192.168.1.69/poll", body=local_poll_json, repeat=True)
        yield m


@pytest.fixture
def mock_cloud_login_flow_connectivity_testing(
    cookies: list[tuple[str, str]],
    enum_locations_json: str,
    enum_fireplaces_json: str,
    cloud_poll_json: str,
    local_poll_json: str,
) -> Generator[aioresponses, None, None]:
    """Test connectivity."""
    with aioresponses() as m:
        # Mock the POST login request
        setup_common_mocks(
            m,
            cookies,
            enum_locations_json,
            enum_fireplaces_json,
            cloud_poll_json,
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


@pytest.fixture
def mock_login_for_control_testing(
    cookies: list[tuple[str, str]],
    enum_locations_json: str,
    enum_fireplaces_json: str,
    cloud_poll_json: str,
    local_poll_json: str,
    challenge_text: str,
) -> Generator[aioresponses, None, None]:
    """Fixture for mocking login process for control testing."""
    # Using 'aioresponses' for mocking asynchronous HTTP responses.
    with aioresponses() as m:
        # Set up common mocks for the test.
        setup_common_mocks(
            m,
            cookies,
            enum_locations_json,
            enum_fireplaces_json,
            cloud_poll_json,
            repeat=False,
        )

        # Mock successful polling of the application.
        m.get(
            "https://iftapi.net/a/XXXXXE834CE109D849CBB15CDDBAFF381//apppoll",
            status=200,
            body=cloud_poll_json,
            repeat=True,
        )

        # Mock successful POST request for cloud-based operations.
        m.post(
            "https://iftapi.net/a/XXXXXE834CE109D849CBB15CDDBAFF381//apppost",
            repeat=True,
            status=204,
        )

        # Mock successful polling of local endpoint.
        m.get("http://192.168.1.69/poll", body=local_poll_json, repeat=True)

        # Mock retrieval of a challenge text from the local endpoint.
        m.get("http://192.168.1.69/get_challenge", body=challenge_text, repeat=True)

        # Mock POST request to the local control endpoint.
        m.post("http://192.168.1.69/post", repeat=True)
        yield m


@pytest.fixture
def mock_login_bad_credentials() -> Generator[aioresponses, None, None]:
    """Fixture for mocking a login process with bad credentials."""
    # Using 'aioresponses' to mock asynchronous HTTP responses.
    with aioresponses() as m:
        # Mock a failed login attempt due to bad credentials.
        m.post("https://iftapi.net/a/login", status=403)
        yield m
