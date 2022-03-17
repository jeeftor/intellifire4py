"""Test Case."""
import json
from unittest import TestCase

from intellifire4py import IntellifirePollData
from intellifire4py.const import IntellifireErrorCode

JSON1 = """
    {
  "name": "",
  "serial": "9CE2E834CE109D849CBB15CDDBAFF381",
  "temperature": 18,
  "battery": 0,
  "pilot": 1,
  "light": 0,
  "height": 0,
  "fanspeed": 1,
  "hot": 0,
  "power": 1,
  "thermostat": 0,
  "setpoint": 2100,
  "timer": 0,
  "timeremaining": 0,
  "prepurge": 0,
  "feature_light": 0,
  "feature_thermostat": 1,
  "power_vent": 0,
  "feature_fan": 1,
  "errors": [
    6,642
  ],
  "fw_version": "0x00030100",
  "fw_ver_str": "0.3.1+hw2",
  "downtime": 0,
  "uptime": 648,
  "connection_quality": 984864,
  "ecm_latency": 0,
  "ipv4_address": "192.168.1.80"
}"""

d1 = json.loads(JSON1)
d2 = {
    "name": "",
    "serial": "9CE2E834CE109D849CBB15CDDBAFF381",
    "temperature": 18,
    "battery": 0,
    "pilot": 1,
    "light": 0,
    "height": 0,
    "fanspeed": 1,
    "hot": 0,
    "power": 1,
    "thermostat": 0,
    "setpoint": 2100,
    "timer": 0,
    "timeremaining": 0,
    "prepurge": 0,
    "feature_light": 0,
    "feature_thermostat": 1,
    "power_vent": 0,
    "feature_fan": 1,
    "errors": [],
    "fw_version": "0x00030100",
    "fw_ver_str": "0.3.1+hw2",
    "downtime": 0,
    "uptime": 840,
    "connection_quality": 987104,
    "ecm_latency": 0,
    "ipv4_address": "192.168.1.80",
}


class TestIntellifire(TestCase):
    """Test case."""

    def test_poll(self) -> None:
        """Test Parsing."""
        print(d2)
        print(d1)

        try:
            d = IntellifirePollData.parse_obj(d1)
            assert d.error_codes[0] == IntellifireErrorCode.FAN_DELAY
            assert d.error_codes[1] == IntellifireErrorCode.OFFLINE

            assert ", ".join([x.name for x in d.error_codes]) == "FAN_DELAY, OFFLINE"

            assert (
                d.error_codes_string
                == ", ".join([x.name for x in d.error_codes])
                == "FAN_DELAY, OFFLINE"
            )

            assert d.error_fan_delay is True
            assert d.error_offline is True
            assert d.error_accessory is False

        except:  # noqa: E722
            self.fail("Couldn't parse D1")

        try:
            IntellifirePollData.parse_obj(d2)
        except:  # noqa: E722
            self.fail("Couldn't parse D2")
