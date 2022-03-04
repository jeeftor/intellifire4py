"""Intellifire 4 Python."""
from __future__ import annotations

from intellifire4py.const import IntellifireErrorCode
from intellifire4py.control_async import IntellifireControlAsync
from intellifire4py.intellifire_async import IntellifireAsync
from intellifire4py.model import (
    IntellifireFireplace,
    IntellifireFireplaces,
    IntellifireLocationDetails,
    IntellifireLocations,
    IntellifirePollData,
)
from intellifire4py.udp import AsyncUDPFireplaceFinder, UDPFireplaceFinder


class ApiCallException(Exception):
    """Error with the API call."""


class InputRangeException(Exception):
    """Input out of bounds."""

    def __init__(self, field: str, min_value: int, max_value: int):
        """Initialize the exception."""
        self.message = (
            f"{field} is out of bounds: valid values [{min_value}:{max_value}]"
        )
        super().__init__(self.message)


class LoginException(Exception):
    """Failure with the login process."""
