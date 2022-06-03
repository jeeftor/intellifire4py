"""Test File."""
import os

from pydantic import ValidationError

from intellifire4py import IntellifirePollData


def test_json_files() -> None:
    """Test Function."""
    base_path = os.path.dirname(os.path.realpath(__file__))
    for file_name in [base_path + "/test1.json", base_path + "/error_6.json"]:
        file = open(file_name)
        json_str = file.read()
        try:
            IntellifirePollData.parse_raw(json_str)
        except ValidationError as e:
            print(e)
