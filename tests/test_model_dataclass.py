"""Low-hanging fruit: Cover IntelliFirePollData in model.py."""
from intellifire4py.model import IntelliFirePollData

def test_poll_data_properties():
    d = IntelliFirePollData()
    # Access all properties and methods
    assert d.temperature_f == (d.temperature_c * 9 / 5) + 32
    assert d.thermostat_setpoint_c == d.raw_thermostat_setpoint / 100
    assert d.thermostat_setpoint_f == (d.raw_thermostat_setpoint / 100 * 9 / 5) + 32
    # error_codes and error_codes_string
    assert isinstance(d.error_codes, list)
    assert isinstance(d.error_codes_string, str)
    # Dict and JSON
    as_dict = d.dict()
    as_json = d.json()
    assert isinstance(as_dict, dict)
    assert isinstance(as_json, str)
    # Test instantiation with some fields
    d2 = IntelliFirePollData(battery=5, temperature=21, setpoint=2300, errors=[2, 4])
    assert d2.battery == 5
    assert d2.temperature_c == 21
    assert d2.raw_thermostat_setpoint == 2300
    assert len(d2.error_codes) == 2
