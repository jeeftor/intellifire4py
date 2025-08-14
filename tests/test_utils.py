"""Tests for utils.py."""

from unittest import TestCase
from intellifire4py.utils import _range_check, _convert_aiohttp_response_to_curl
from intellifire4py.const import IntelliFireCommand
from intellifire4py.exceptions import InputRangError
import pytest


class TestRangeCheck(TestCase):
    """Test cases for the _range_check function."""

    def test_valid_range(self) -> None:
        """Test with a valid value within the range."""
        command = IntelliFireCommand.POWER
        value = 1
        try:
            _range_check(command, value)
        except InputRangError as e:
            self.fail(f"Unexpected InputRangError: {e}")

    def test_value_below_min(self) -> None:
        """Test with a value below the minimum allowed."""
        command = IntelliFireCommand.POWER
        value = -1
        with self.assertRaises(InputRangError) as context:
            _range_check(command, value)
        self.assertEqual(
            str(context.exception), "POWER is out of bounds: valid values [0:1]"
        )

    def test_value_above_max(self) -> None:
        """Test with a value above the maximum allowed."""
        command = IntelliFireCommand.POWER
        value = 2
        with self.assertRaises(InputRangError) as context:
            _range_check(command, value)
        self.assertEqual(
            str(context.exception), "POWER is out of bounds: valid values [0:1]"
        )

    def test_valid_range_max_min_edge_case(self) -> None:
        """Test with a value at the edge case of the valid range."""
        command = IntelliFireCommand.POWER
        min_value: int = command.value["min"]  # type: ignore
        max_value: int = command.value["max"]  # type: ignore
        value = (max_value + min_value) // 2
        try:
            _range_check(command, value)
        except InputRangError as e:
            self.fail(f"Unexpected InputRangError: {e}")

    def test_valid_range_max_plus_one(self) -> None:
        """Test with a value one greater than the maximum allowed."""
        command = IntelliFireCommand.POWER
        max_value: int = command.value["max"]  # type: ignore
        value = max_value + 1
        with self.assertRaises(InputRangError) as context:
            _range_check(command, value)
        self.assertEqual(
            str(context.exception), "POWER is out of bounds: valid values [0:1]"
        )

    def test_valid_range_min_minus_one(self) -> None:
        """Test with a value one less than the minimum allowed."""
        command = IntelliFireCommand.POWER
        min_value: int = command.value["min"]  # type: ignore
        value = min_value - 1
        with self.assertRaises(InputRangError) as context:
            _range_check(command, value)
        self.assertEqual(
            str(context.exception), "POWER is out of bounds: valid values [0:1]"
        )

    @pytest.mark.asyncio
    async def test_convert_aiohttp_response_to_curl(self):
        """Test conversion of aiohttp response to curl command."""

        class DummyRequestInfo:
            method = "POST"
            headers = {"Content-Type": "application/json", "X-Test": "foo"}
            url = "http://localhost/api"

        class DummyResponse:
            request_info = DummyRequestInfo()
            url = "http://localhost/api"

            async def read(self):
                return b'{"foo": "bar"}'

        curl = await _convert_aiohttp_response_to_curl(DummyResponse())
        assert "curl -X POST" in curl
        assert '-H "Content-Type: application/json"' in curl
        assert '-d \'{"foo": "bar"}\'' in curl
        assert "http://localhost/api" in curl
