"""Shared config file."""
import os

import pytest


@pytest.fixture
def poll_response_text() -> str:
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
