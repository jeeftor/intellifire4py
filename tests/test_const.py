"""Basic error code test case."""
from unittest import TestCase

from intellifire4py.const import IntellifireErrorCode


class TestErrors(TestCase):
    """Test Case."""

    def test_errors(self):
        """Test Function."""
        e = IntellifireErrorCode(642)
        assert e == IntellifireErrorCode.OFFLINE
