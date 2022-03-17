"""Test File."""
from pydantic import ValidationError

from intellifire4py import IntellifirePollData


def test_json_files() -> None:
    """Test Function."""
    for file_name in ["test1.json", "error_6.json"]:
        file = open(file_name)
        json_str = file.read()
        try:
            IntellifirePollData.parse_raw(json_str)
        except ValidationError as e:
            print(e)
