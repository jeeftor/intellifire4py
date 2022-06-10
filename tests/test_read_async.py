import asyncio
import json
import os
from json import JSONDecodeError
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ServerDisconnectedError
from asynctest import CoroutineMock

from intellifire4py.read_async import IntellifireAsync


class MockResponse:
    def __init__(self, text, status):
        self._text = text
        self.status = status

    async def text(self):
        return self._text

    async def json(self, _):
        return self._text

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self


@patch("intellifire4py.intellifire.aiohttp.ClientSession.get")
@pytest.mark.asyncio
async def test_poll_good(mock_get):
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
@pytest.mark.asyncio
async def test_poll_connection_errror1(mock_get):
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
@pytest.mark.asyncio
async def test_poll_bad_json(mock_get):
    base_path = os.path.dirname(os.path.realpath(__file__))
    file = open(base_path + "/test1.json")
    json_str = file.read()

    mock_get.return_value.__aenter__.return_value.json = CoroutineMock()
    mock_get.return_value.__aenter__.return_value.status = 200
    # mock_get.return_value.__aenter__.return_value.json.return_value = None
    mock_get.return_value.__aenter__.return_value.json.side_effect = JSONDecodeError(
        "msg", "doc", 3
    )

    i = IntellifireAsync(ip="192.168.1.2")
    await i.poll()

    assert i.data is None
