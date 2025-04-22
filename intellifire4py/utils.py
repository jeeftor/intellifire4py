"""Utility functions."""

from .const import IntelliFireCommand
from .exceptions import InputRangError


def _range_check(command: IntelliFireCommand, value: int) -> None:
    """Perform a value range check.

    Args:
        command (IntelliFireCommand): The command enum.
        value (int): The value to be checked.

    Raises:
        InputRangError: If the value is not within the specified range.
    """
    min_value: int = command.value["min"]  # type: ignore
    max_value: int = command.value["max"]  # type: ignore

    if value > max_value or value < min_value:
        raise InputRangError(
            field=str(command.name),
            min_value=min_value,
            max_value=max_value,
        )


async def _convert_aiohttp_response_to_curl(response) -> str:
    # Get the request details from the response
    method = response.request_info.method
    headers = response.request_info.headers
    body = await response.read()

    # Build the curl command
    curl_command = f"curl -X {method} \\\n"

    # Add headers to the curl command
    for header, value in headers.items():
        curl_command += f'    -H "{header}: {value}" \\\n'

    # Add the request body if present
    if body:
        curl_command += f'    -d \'{body.decode("utf-8")}\' \\\n'

    # Add the URL
    curl_command += f"    {response.url}"

    return curl_command
