"""Basic error code test case."""
from unittest import TestCase

from intellifire4py.const import IntellifireErrorCode


class TestErrors(TestCase):
    """Test Case."""

    def test_errors(self) -> None:
        """Test Function."""

        e = IntellifireErrorCode(642)
        assert e == IntellifireErrorCode.OFFLINE

        assert IntellifireErrorCode(2) == IntellifireErrorCode(130)
        assert IntellifireErrorCode.FLAME == IntellifireErrorCode(4)
        assert IntellifireErrorCode.FAN_DELAY == IntellifireErrorCode(6)
        assert IntellifireErrorCode.MAINTENANCE == IntellifireErrorCode(64)
        assert IntellifireErrorCode.DISABLED == IntellifireErrorCode(129)
        assert IntellifireErrorCode.DISABLED == IntellifireErrorCode(145)
        assert IntellifireErrorCode.FAN == IntellifireErrorCode(132)
        assert IntellifireErrorCode.LIGHTS == IntellifireErrorCode(133)
        assert IntellifireErrorCode.ACCESSORY == IntellifireErrorCode(134)
        assert IntellifireErrorCode.SOFT_LOCK_OUT == IntellifireErrorCode(144)
        assert IntellifireErrorCode.ECM_OFFLINE == IntellifireErrorCode(3269)
        assert IntellifireErrorCode.OFFLINE == IntellifireErrorCode(642)

    def test_messages(self) -> None:
        """Test error messages."""
        assert (
            IntellifireErrorCode.PILOT_FLAME.get_message()  # type: ignore
            == "Pilot Flame Error: Your appliance has been safely disabled. Please contact your dealer and report this issue."
        )
        assert (
            IntellifireErrorCode.FAN_DELAY.get_message()  # type: ignore
            == "Fan Information: Fan will turn on within 3 minutes. Your appliance has a built-in delay that prevents the fan from operating within the first 3 minutes of turning on the appliance. This allows the air to be heated prior to circulation."
        )
        assert (
            IntellifireErrorCode.FLAME.get_message()  # type: ignore
            == "Pilot Flame Error. Your appliance has been safely disabled. Please contact your dealer and report this issue."
        )
        assert (
            IntellifireErrorCode.MAINTENANCE.get_message()  # type: ignore
            == "Maintenance: Your appliance is due for a routine maintenance check. Please contact your dealer to ensure your appliance is operating at peak performance."
        )
        assert (
            IntellifireErrorCode.DISABLED.get_message()  # type: ignore
            == "Appliance Safely Disabled: Your appliance has been disabled. Please contact your dealer and report this issue."
        )
        assert (
            IntellifireErrorCode.FAN.get_message()  # type: ignore
            == "Fan Error. Your appliance has detected that an accessory is not functional. Please contact your dealer and report this issue."
        )
        assert (
            IntellifireErrorCode.LIGHTS.get_message()  # type: ignore
            == "Lights Error. Your appliance has detected that an accessory is not functional. Please contact your dealer and report this issue."
        )
        assert (
            IntellifireErrorCode.ACCESSORY.get_message()  # type: ignore
            == "Your appliance has detected that an AUX port or accessory is not functional. Please contact your dealer and report this issue."
        )
        assert (
            IntellifireErrorCode.SOFT_LOCK_OUT.get_message()  # type: ignore
            == "Sorry your appliance did not start. Try again by pressing Flame ON."
        )
        assert (
            IntellifireErrorCode.OFFLINE.get_message()  # type: ignore
            == "Your appliance is currently offline."
        )
        assert IntellifireErrorCode.ECM_OFFLINE.get_message() == "ECM is offline."  # type: ignore
