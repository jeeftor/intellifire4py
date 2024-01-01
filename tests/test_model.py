"""Test File."""

try:
    from pydantic.v1 import ValidationError
except ImportError:
    from pydantic import ValidationError  # type: ignore

from intellifire4py.model import IntelliFirePollData


def test_json_files(local_poll_json: str, poll_response_text_error_6_642: str) -> None:
    """Test Function."""
    for json_text in [local_poll_json, poll_response_text_error_6_642]:
        try:
            IntelliFirePollData.parse_raw(json_text)
        except ValidationError as e:
            print(e)
