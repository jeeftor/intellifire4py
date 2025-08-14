"""Shared config file."""

import asyncio
import os
from collections.abc import Generator
from contextlib import ExitStack
from unittest.mock import patch, AsyncMock
import aiohttp

import pytest
from aioresponses import aioresponses

from intellifire4py.const import IntelliFireApiMode
from intellifire4py.model import IntelliFireCommonFireplaceData, IntelliFireUserData


# Define fixtures for various test scenarios.


@pytest.fixture()
def mock_common_data_local(
    api_key, user_id, serial, ip, auth_cookie, web_client_id
) -> IntelliFireCommonFireplaceData:
    """Fixture for mock common data."""
    return IntelliFireCommonFireplaceData(
        auth_cookie=auth_cookie,
        user_id=user_id,
        web_client_id=web_client_id,
        serial=serial,
        api_key=api_key,
        ip_address=ip,
        read_mode=IntelliFireApiMode.LOCAL,
        control_mode=IntelliFireApiMode.LOCAL,
    )


@pytest.fixture
def mock_user_data(
    auth_cookie, user_id, web_client_id, mock_common_data_local
) -> IntelliFireUserData:
    """Fixture for mock user data."""
    return IntelliFireUserData(
        auth_cookie=auth_cookie,
        user_id=user_id,
        web_client_id=web_client_id,
        username="",
        password="",
        fireplaces=[mock_common_data_local],
    )


@pytest.fixture
def mock_common_data_cloud(
    api_key, user_id, serial, ip, auth_cookie, web_client_id
) -> IntelliFireCommonFireplaceData:
    """Fixture for mock common data."""
    return IntelliFireCommonFireplaceData(
        auth_cookie=auth_cookie,
        user_id=user_id,
        web_client_id=web_client_id,
        serial=serial,
        api_key=api_key,
        ip_address=ip,
        read_mode=IntelliFireApiMode.CLOUD,
        control_mode=IntelliFireApiMode.CLOUD,
    )


@pytest.fixture
def mock_common_data_none(
    api_key, user_id, serial, ip, web_client_id, auth_cookie
) -> IntelliFireCommonFireplaceData:
    """Fixture for mock common data."""
    return IntelliFireCommonFireplaceData(
        auth_cookie=auth_cookie,
        user_id=user_id,
        web_client_id=web_client_id,
        serial=serial,
        api_key=api_key,
        ip_address=ip,
        read_mode=IntelliFireApiMode.NONE,
        control_mode=IntelliFireApiMode.NONE,
    )


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
def serial() -> str:
    """Mock serial number."""
    return "XXXXXE834CE109D849CBB15CDDBAFF381"


@pytest.fixture
def ip() -> str:
    """Mock IP address."""
    return "192.168.1.69"


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
def auth_cookie() -> str:
    """Mock auth cookie."""
    return "XXXX1B56D18B52DC8F94DC0E5DC89A90"


@pytest.fixture()
def web_client_id() -> str:
    """Mock web client id."""
    return "XXXX21C9A75384EA726071BFCC95E3F6"


@pytest.fixture
def mock_aioresponse() -> Generator[aioresponses, None, None]:
    """Mock out an aioresponse but i'm not sure if we even use this."""
    # Context manager for mocking aiohttp responses
    with aioresponses() as m:
        yield m


@pytest.fixture
def mock_aiohttp_session():
    """Patch aiohttp.ClientSession for all tests, Home Assistant style.

    Yields:
        mock_session: a mock ClientSession with AsyncMock get/post methods.
    """
    with patch("aiohttp.ClientSession", new_callable=AsyncMock) as session_cls:
        mock_session = session_cls.return_value
        # Configure get and post as async context managers
        mock_session.get = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value.status = 200
        mock_session.get.return_value.__aexit__.return_value = None
        mock_session.post = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value.status = 204
        mock_session.post.return_value.__aexit__.return_value = None
        yield mock_session


def setup_common_mocks(
    m: aioresponses,
    serial: str,
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
        f"https://iftapi.net/a/{serial}//apppoll",
        status=200,
        body=cloud_poll_json,
        repeat=repeat,
    )


@pytest.fixture
def mock_cloud_login_flow_no_local(
    cookies: list[tuple[str, str]],
    enum_locations_json: str,
    enum_fireplaces_json: str,
    cloud_poll_json: str,
    local_poll_json: str,
    serial: str,
    ip: str,
) -> Generator[aioresponses, None, None]:
    """Mock the login flow."""
    with aioresponses() as m:
        setup_common_mocks(
            m,
            serial,
            cookies,
            enum_locations_json,
            enum_fireplaces_json,
            cloud_poll_json,
            repeat=True,
        )
        yield m


@pytest.fixture
def mock_login_flow_with_local_and_cloud(
    cookies: list[tuple[str, str]],
    enum_locations_json: str,
    enum_fireplaces_json: str,
    cloud_poll_json: str,
    local_poll_json: str,
    serial: str,
    ip: str,
) -> Generator[aioresponses, None, None]:
    """Mock the login flow."""
    with aioresponses() as m:
        setup_common_mocks(
            m,
            serial,
            cookies,
            enum_locations_json,
            enum_fireplaces_json,
            cloud_poll_json,
            repeat=True,
        )
        m.get(url=f"http://{ip}/poll", body=local_poll_json, repeat=True)
        yield m


@pytest.fixture
def mock_login_flow_with_cloud_only(
    cookies: list[tuple[str, str]],
    enum_locations_json: str,
    enum_fireplaces_json: str,
    cloud_poll_json: str,
    local_poll_json: str,
    serial: str,
    ip: str,
) -> Generator[aioresponses, None, None]:
    """Mock the login flow."""
    with aioresponses() as m:
        setup_common_mocks(
            m,
            serial,
            cookies,
            enum_locations_json,
            enum_fireplaces_json,
            cloud_poll_json,
            repeat=True,
        )
        m.get(url=f"http://{ip}/poll", status=404, repeat=True)
        yield m


@pytest.fixture
def mock_cloud_login_flow_connectivity_testing(
    cookies: list[tuple[str, str]],
    enum_locations_json: str,
    enum_fireplaces_json: str,
    cloud_poll_json: str,
    local_poll_json: str,
    serial: str,
    ip: str,
) -> Generator[aioresponses, None, None]:
    """Test connectivity."""
    with aioresponses() as m:
        # Mock the POST login request
        setup_common_mocks(
            m,
            serial,
            cookies,
            enum_locations_json,
            enum_fireplaces_json,
            cloud_poll_json,
            repeat=False,
        )

        # Double 404
        m.get(
            f"https://iftapi.net/a/{serial}//apppoll",
            status=404,
            # body=cloud_poll_json,
            # repeat=False,
        )
        m.get(
            url=f"http://{ip}/poll",
            status=404,
        )

        # 403 / timeout
        m.get(
            f"https://iftapi.net/a/{serial}//apppoll",
            status=403,  # bad credentials
        )
        m.get(
            url=f"http://{ip}/poll",
            body=None,
            exception=asyncio.TimeoutError(),
        )

        # All is finally good
        m.get(
            f"https://iftapi.net/a/{serial}//apppoll",
            status=200,
            body=cloud_poll_json,
            repeat=False,
        )
        m.get(
            url=f"http://{ip}/poll",
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
    serial: str,
    ip: str,
) -> Generator[aioresponses, None, None]:
    """Fixture for mocking login process for control testing."""
    # Using 'aioresponses' for mocking asynchronous HTTP responses.
    with aioresponses() as m:
        # Set up common mocks for the test.
        setup_common_mocks(
            m,
            serial,
            cookies,
            enum_locations_json,
            enum_fireplaces_json,
            cloud_poll_json,
            repeat=False,
        )

        # Mock successful polling of the application.
        m.get(
            f"https://iftapi.net/a/{serial}//apppoll",
            status=200,
            body=cloud_poll_json,
            repeat=True,
        )

        # Mock successful POST request for cloud-based operations.
        m.post(
            f"https://iftapi.net/a/{serial}//apppost",
            repeat=True,
            status=204,
        )

        # Mock successful polling of local endpoint.
        m.get(f"http://{ip}/poll", body=local_poll_json, repeat=True)

        # Mock retrieval of a challenge text from the local endpoint.
        m.get(f"http://{ip}/get_challenge", body=challenge_text, repeat=True)

        # Mock POST request to the local control endpoint.
        m.post(f"http://{ip}/post", repeat=True)
        yield m


@pytest.fixture
def mock_login_bad_credentials() -> Generator[aioresponses, None, None]:
    """Fixture for mocking a login process with bad credentials."""
    # Using 'aioresponses' to mock asynchronous HTTP responses.
    with aioresponses() as m:
        # Mock a failed login attempt due to bad credentials.
        m.post("https://iftapi.net/a/login", status=403)
        yield m


@pytest.fixture
def mock_background_polling() -> Generator:
    """Fixture for mocking background polling."""
    with ExitStack() as stack:
        local_stop_mock = stack.enter_context(
            patch("intellifire4py.IntelliFireAPILocal.stop_background_polling")
        )
        cloud_stop_mock = stack.enter_context(
            patch("intellifire4py.IntelliFireAPICloud.stop_background_polling")
        )
        # abstract_stop_mock = stack.enter_context(
        #     patch("intellifire4py.IntelliFireDataProvider.stop_background_polling")
        # )
        local_start_mock = stack.enter_context(
            patch("intellifire4py.IntelliFireAPILocal.start_background_polling")
        )
        cloud_start_mock = stack.enter_context(
            patch("intellifire4py.IntelliFireAPICloud.start_background_polling")
        )
        # abstract_start_mock = stack.enter_context(
        #     patch("intellifire4py.IntelliFireDataProvider.start_background_polling")
        # )

        yield {
            "local_stop": local_stop_mock,
            "cloud_stop": cloud_stop_mock,
            # "abstract_stop": abstract_stop_mock,
            "local_start": local_start_mock,
            "cloud_start": cloud_start_mock,
            # "abstract_start": abstract_start_mock,
        }


@pytest.fixture
def mock_cloud_api():
    """Patch IntelliFireAPICloud internals for cloud API tests using autospec and correct method names."""
    from unittest.mock import patch, AsyncMock

    with (
        patch(
            "intellifire4py.cloud_api.IntelliFireAPICloud.send_command",
            new_callable=AsyncMock,
        ) as send_command,
        patch(
            "intellifire4py.cloud_api.IntelliFireAPICloud._send_cloud_command",
            new_callable=AsyncMock,
        ) as _send_cloud_command,
        patch(
            "intellifire4py.cloud_api.IntelliFireAPICloud.poll", new_callable=AsyncMock
        ) as poll,
        patch("intellifire4py.cloud_api._range_check") as _range_check,
    ):

        class Mocks:
            pass

        mocks = Mocks()
        mocks.send_command = send_command
        mocks._send_cloud_command = _send_cloud_command
        mocks.poll = poll
        mocks._range_check = _range_check
        yield mocks


@pytest.fixture
def fake_error_session_factory():
    """Factory fixture to create a FakeSession that raises for given status code (GET/POST).

    Usage: session = fake_error_session_factory(status_code, method="get"|"post")
    """

    def _factory(status_code, method="get"):
        class FakeResponse:
            status = status_code

            async def json(self):
                return {}

            def raise_for_status(self):
                raise aiohttp.ClientResponseError(None, (), status=status_code)

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                pass

        class FakeSession:
            async def get(self, *a, **kw):
                return FakeResponse()

            async def post(self, *a, **kw):
                return FakeResponse()

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                pass

        return FakeSession()

    return _factory


@pytest.fixture(params=[403, 404, 500])
def fake_error_session(request, fake_error_session_factory):
    """Parametrized fixture for sessions that raise for 403, 404, or 500 status codes.

    Usage: pass fake_error_session as a test argument for error handling coverage.
    """
    return fake_error_session_factory(request.param)


@pytest.fixture
# NOTE: This fixture is intentionally NOT async. AsyncMock handles async patching.
def mock_async_validate_connectivity():
    """Fixture to patch UnifiedFireplace.async_validate_connectivity with an AsyncMock for async method mocking in tests."""
    with patch(
        "intellifire4py.unified_fireplace.UnifiedFireplace.async_validate_connectivity",
        new_callable=AsyncMock,
    ) as mock:
        yield mock
