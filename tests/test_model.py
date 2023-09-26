"""Test File."""

from pydantic import ValidationError

from src.intellifire4py.model import IntelliFirePollData


def test_json_files(
    poll_response_text: str, poll_response_text_error_6_642: str
) -> None:
    """Test Function."""
    for json_text in [poll_response_text, poll_response_text_error_6_642]:
        try:
            IntelliFirePollData.parse_raw(json_text)
        except ValidationError as e:
            print(e)
