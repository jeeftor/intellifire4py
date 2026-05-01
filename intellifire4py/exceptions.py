"""IntelliFire Exceptions."""


class CloudError(Exception):
    """Error with the API call."""


class CommandError(Exception):
    """Base error for command failures."""


class MissingCredentialsError(CommandError):
    """Command cannot be sent because credentials are missing."""


class CommandRejectedError(CommandError):
    """Fireplace or cloud service rejected a command."""


class CommandRetryError(CommandError):
    """Command could not be sent after retry attempts."""


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
