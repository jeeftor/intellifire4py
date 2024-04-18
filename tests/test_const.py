"""Basic error code test case."""

from unittest import TestCase

from intellifire4py.const import IntelliFireErrorCode


class TestErrors(TestCase):
    """Test Case."""

    def test_errors(self) -> None:
        """Test Function."""
        e = IntelliFireErrorCode(642)
        assert e == IntelliFireErrorCode.OFFLINE

        assert IntelliFireErrorCode(2) == IntelliFireErrorCode(130)
        assert IntelliFireErrorCode.FLAME == IntelliFireErrorCode(4)
        assert IntelliFireErrorCode.FAN_DELAY == IntelliFireErrorCode(6)
        assert IntelliFireErrorCode.MAINTENANCE == IntelliFireErrorCode(64)
        assert IntelliFireErrorCode.DISABLED == IntelliFireErrorCode(129)
        assert IntelliFireErrorCode.DISABLED == IntelliFireErrorCode(145)
        assert IntelliFireErrorCode.FAN == IntelliFireErrorCode(132)
        assert IntelliFireErrorCode.LIGHTS == IntelliFireErrorCode(133)
        assert IntelliFireErrorCode.ACCESSORY == IntelliFireErrorCode(134)
        assert IntelliFireErrorCode.SOFT_LOCK_OUT == IntelliFireErrorCode(144)
        assert IntelliFireErrorCode.ECM_OFFLINE == IntelliFireErrorCode(3269)
        assert IntelliFireErrorCode.OFFLINE == IntelliFireErrorCode(642)

    def test_messages(self) -> None:
        """Test error messages."""
        assert (
            IntelliFireErrorCode.PILOT_FLAME.get_message()  # type: ignore
            == "Pilot Flame Error: Your appliance has been safely disabled. Please contact your dealer and report this issue."
        )
        assert (
            IntelliFireErrorCode.FAN_DELAY.get_message()  # type: ignore
            == "Fan Information: Fan will turn on within 3 minutes. Your appliance has a built-in delay that prevents the fan from operating within the first 3 minutes of turning on the appliance. This allows the air to be heated prior to circulation."
        )
        assert (
            IntelliFireErrorCode.FLAME.get_message()  # type: ignore
            == "Pilot Flame Error. Your appliance has been safely disabled. Please contact your dealer and report this issue."
        )
        assert (
            IntelliFireErrorCode.MAINTENANCE.get_message()  # type: ignore
            == "Maintenance: Your appliance is due for a routine maintenance check. Please contact your dealer to ensure your appliance is operating at peak performance."
        )
        assert (
            IntelliFireErrorCode.DISABLED.get_message()  # type: ignore
            == "Appliance Safely Disabled: Your appliance has been disabled. Please contact your dealer and report this issue."
        )
        assert (
            IntelliFireErrorCode.FAN.get_message()  # type: ignore
            == "Fan Error. Your appliance has detected that an accessory is not functional. Please contact your dealer and report this issue."
        )
        assert (
            IntelliFireErrorCode.LIGHTS.get_message()  # type: ignore
            == "Lights Error. Your appliance has detected that an accessory is not functional. Please contact your dealer and report this issue."
        )
        assert (
            IntelliFireErrorCode.ACCESSORY.get_message()  # type: ignore
            == "Your appliance has detected that an AUX port or accessory is not functional. Please contact your dealer and report this issue."
        )
        assert (
            IntelliFireErrorCode.SOFT_LOCK_OUT.get_message()  # type: ignore
            == "Sorry your appliance did not start. Try again by pressing Flame ON."
        )
        assert (
            IntelliFireErrorCode.OFFLINE.get_message()  # type: ignore
            == "Your appliance is currently offline."
        )
        assert IntelliFireErrorCode.ECM_OFFLINE.get_message() == "ECM is offline."  # type: ignore
