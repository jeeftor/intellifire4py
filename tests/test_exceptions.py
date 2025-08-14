"""Test exceptions for intellifire4py."""

import pytest
from intellifire4py.exceptions import CloudError, InputRangError


def test_cloud_error():
    """Test CloudError exception."""
    with pytest.raises(CloudError):
        raise CloudError("API call failed")


def test_input_range_error():
    """Test InputRangError exception."""
    err = InputRangError("field", 1, 10)
    assert isinstance(err, InputRangError)
    assert "field is out of bounds: valid values [1:10]" in str(err)
    # And raising
    with pytest.raises(InputRangError):
        raise err
