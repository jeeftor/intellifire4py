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
