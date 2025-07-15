"""Test File."""

from pydantic import ValidationError

from intellifire4py.model import IntelliFirePollData


def test_json_files(local_poll_json: str, poll_response_text_error_6_642: str) -> None:
    """Test Function."""
    for json_text in [local_poll_json, poll_response_text_error_6_642]:
        try:
            IntelliFirePollData.model_validate_json(json_text)
        except ValidationError as e:
            print(e)


def test_jsons(cloud_poll_json, local_poll_json):
    """Test Function."""
    cloud = IntelliFirePollData.model_validate_json(cloud_poll_json)
    local = IntelliFirePollData.model_validate_json(local_poll_json)
    assert cloud.battery == local.battery

    assert cloud.brand == "H&G"
    assert local.brand == "unset"
    assert cloud.ecm_latency == local.ecm_latency

    assert local.fanspeed == 1
    assert cloud.fanspeed == 0
    assert cloud.has_fan == local.has_fan
    assert cloud.has_light is False
    assert local.has_light is True
    assert cloud.has_thermostat is True
    assert local.has_thermostat is True

    assert cloud.flameheight == 4 == local.flameheight

    assert cloud.is_hot == False == local.is_hot  # noqa: E712
    assert cloud.ipv4_address == local.ipv4_address
    assert cloud.has_light != local.has_light
    assert cloud.name == "Living Room"
    assert local.name == ""

    assert cloud.pilot_on != local.pilot_on
    assert cloud.is_on == local.is_on
    assert cloud.has_power_vent == local.has_power_vent == False  # noqa E712
    assert cloud.prepurge == local.prepurge

    assert cloud.temperature_c == 17 == local.temperature_c
    assert cloud.temperature_f == local.temperature_f

    assert cloud.has_thermostat == local.has_thermostat
    assert cloud.has_errors == local.has_errors
    # assert cloud.thermostat == local.thermostat
    # assert cloud.timer == local.timer
    # assert cloud.timeremaining == local.timeremaining

    # Alias differences
    assert cloud.downtime == 2
    assert local.downtime == 3

    assert cloud.connection_quality == 987690
    assert local.connection_quality == 995871
    assert cloud.fw_version == "0x00030200"
    assert local.fw_version == "0x01030000"
    assert cloud.fw_ver_str == "0.3.2+hw2"
    assert local.fw_ver_str == "1.3.0"
    assert cloud.uptime == 389
    assert local.uptime == 3362
    assert cloud.raw_thermostat_setpoint == 16
    assert local.raw_thermostat_setpoint == 17

    assert local.thermostat_setpoint_c == 0.17
    assert local.thermostat_setpoint_f == 32.306
    assert local.error_codes_string == ""
    assert local.error_codes == []

    assert local.error_codes_string == ""
    assert local.error_pilot_flame is False
    assert local.error_flame is False
    assert local.error_fan_delay is False
    assert local.error_maintenance is False
    assert local.error_disabled is False
    assert local.error_fan is False
    assert local.error_lights is False
    assert local.error_accessory is False
    assert local.error_soft_lock_out is False
    assert local.error_ecm_offline is False
    assert local.error_offline is False
