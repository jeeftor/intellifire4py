"""Utility functions."""
from intellifire4py.const import IntelliFireCommand
from intellifire4py.exceptions import InputRangError


def _range_check(command: IntelliFireCommand, value: int) -> None:
    """Perform a value range check."""
    # Validate the range on input
    min_value: int = command.value["min"]  # type: ignore
    max_value: int = command.value["max"]  # type: ignore

    if value > max_value or value < min_value:
        raise InputRangError(
            field=str(command.name),
            min_value=min_value,
            max_value=max_value,
        )
