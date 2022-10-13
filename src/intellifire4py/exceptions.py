"""IntelliFire Exceptions."""


class ApiCallError(Exception):
    """Error with the API call."""


class InputRangError(Exception):
    """Input out of bounds."""

    def __init__(self, field: str, min_value: int, max_value: int):
        """Initialize the exception."""
        self.message = (
            f"{field} is out of bounds: valid values [{min_value}:{max_value}]"
        )
        super().__init__(self.message)


class LoginError(Exception):
    """Failure with the login process."""
