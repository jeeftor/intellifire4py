"""Conftest file which I dont understand completely."""

import pytest
from aioresponses import aioresponses


@pytest.fixture
def mock_aioresponse():  # type: ignore
    """Mock aioresponse."""
    with aioresponses() as m:
        yield m
