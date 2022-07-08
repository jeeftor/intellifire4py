"""Read async tests."""
import json
import os
from json import JSONDecodeError
from typing import Any
from unittest.mock import patch

import pytest
from asynctest import CoroutineMock

from intellifire4py.read_async import IntellifireAsync


class MockResponse:
    """Mock response class."""

    def __init__(self, text: str, status: int) -> None:
        """Create a mock response."""
        self._text = text
        self.status = status

    async def text(self) -> str:
        """Text return."""
        return self._text

    async def json(self, _: Any) -> str:
        """Json Return."""
        return self._text

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        """Exit function."""
        pass

    async def __aenter__(self):  # type: ignore
        """Enter function."""
        return self


@patch("intellifire4py.intellifire.aiohttp.ClientSession.get")
@pytest.mark.asyncio  # type: ignore
async def test_poll_good(mock_get) -> None:  # type: ignore
    """Test for good poll results."""
    base_path = os.path.dirname(os.path.realpath(__file__))
    file = open(base_path + "/test1.json")
    json_str = file.read()

    mock_get.return_value.__aenter__.return_value.json = CoroutineMock()
    mock_get.return_value.__aenter__.return_value.status = 200
    mock_get.return_value.__aenter__.return_value.json.return_value = json.loads(
        json_str
    )

    i = IntellifireAsync(ip="192.168.1.2")
    await i.poll()

    assert i.data is not None


@patch("intellifire4py.intellifire.aiohttp.ClientSession.get")
@pytest.mark.asyncio  # type: ignore
async def test_poll_connection_error1(mock_get) -> None:  # type: ignore
    """Run an error test."""
    base_path = os.path.dirname(os.path.realpath(__file__))
    file = open(base_path + "/test1.json")
    json_str = file.read()

    mock_get.return_value.__aenter__.return_value.json = CoroutineMock()
    mock_get.return_value.__aenter__.return_value.status = 404
    mock_get.return_value.__aenter__.return_value.json.return_value = json.loads(
        json_str
    )

    i = IntellifireAsync(ip="192.168.1.2")
    await i.poll()

    assert i.data is None


@patch("intellifire4py.intellifire.aiohttp.ClientSession.get")
@pytest.mark.asyncio  # type: ignore
async def test_poll_bad_json(mock_get) -> None:  # type: ignore
    """Bad test."""
    # base_path = os.path.dirname(os.path.realpath(__file__))
    # file = open(base_path + "/test1.json")

    mock_get.return_value.__aenter__.return_value.json = CoroutineMock()
    mock_get.return_value.__aenter__.return_value.status = 200
    # mock_get.return_value.__aenter__.return_value.json.return_value = None
    mock_get.return_value.__aenter__.return_value.json.side_effect = JSONDecodeError(
        "msg", "doc", 3
    )

    i = IntellifireAsync(ip="192.168.1.2")
    await i.poll()

    assert i.data is None
