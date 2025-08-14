"""Test cloud functions."""

import pytest

# from httpx import Cookies

from intellifire4py import UnifiedFireplace
from intellifire4py.cloud_interface import IntelliFireCloudInterface
from intellifire4py.const import IntelliFireApiMode
from intellifire4py.exceptions import LoginError


@pytest.mark.asyncio
async def test_cloud_login(  # type: ignore
    mock_cloud_login_flow_no_local,
    user_id,
    api_key,
):
    """Test cloud login."""
    username = "user"
    password = "pass"  # noqa: S105

    async with IntelliFireCloudInterface() as cloud_interface:
        await cloud_interface.login_with_credentials(
            username=username, password=password
        )
        user_data = cloud_interface.user_data
        fireplaces = await UnifiedFireplace.build_fireplaces_from_user_data(
            user_data,
            desired_control_mode=IntelliFireApiMode.NONE,
            desired_read_mode=IntelliFireApiMode.NONE,
        )
        fireplace = fireplaces[0]
        await fireplace.perform_cloud_poll()
        assert fireplace.serial == "XXXXXE834CE109D849CBB15CDDBAFF381"
        assert fireplace.data.brand == "H&G"
        assert fireplace.data.name == "Living Room"
        assert fireplace.api_key == api_key
        assert fireplace.data.is_on is False
        assert fireplace.data.pilot_on is True

        assert cloud_interface.user_data.user_id == user_id


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_control(  # type: ignore
    mock_login_for_control_testing,
    user_id: str,
    api_key: str,
) -> None:  # Build cookies
    """Test control."""
    username = "user"
    password = "pass"  # noqa: S105
    async with IntelliFireCloudInterface() as cloud_interface:
        await cloud_interface.login_with_credentials(
            username=username, password=password
        )
        user_data = cloud_interface.user_data
        fireplaces = await UnifiedFireplace.build_fireplaces_from_user_data(
            user_data,
            desired_control_mode=IntelliFireApiMode.CLOUD,
            desired_read_mode=IntelliFireApiMode.CLOUD,
        )
        fp = fireplaces[0]

        assert fp.data.serial == "unset"
        assert fp.data.brand == "H&G"
        assert fp.data.battery == 0
        assert fp.data.connection_quality == 987690
        await fp.read_api.start_background_polling()

        assert fp.read_api.is_polling_in_background is True

        await fp.control_api.pilot_on()
        assert fp.data.pilot_on is True
        await fp.control_api.flame_on()
        assert fp.data.is_on is True
        await fp.control_api.flame_off()
        await fp.control_api.soft_reset()
        await fp.control_api.stop_sleep_timer()
        await fp.control_api.set_thermostat_c(10)
        await fp.control_api.set_thermostat_f(70)
        await fp.control_api.turn_on_thermostat()
        await fp.control_api.turn_off_thermostat()
        await fp.control_api.fan_off()
        await fp.control_api.beep()
        assert fp.data.is_on is False
        assert fp.read_api.is_polling_in_background is True
        assert fp.read_api.data.name == "Living Room"
        await fp.read_api.stop_background_polling()


@pytest.mark.asyncio
async def test_incorrect_login_credentials(mock_login_bad_credentials) -> None:  # type: ignore
    """Test login with incorrect credentials."""
    username = "incorrect_user"
    password = "incorrect_password"  # noqa S105)

    async with IntelliFireCloudInterface() as cloud_interface:
        with pytest.raises(LoginError):
            await cloud_interface.login_with_credentials(
                username=username, password=password
            )


@pytest.mark.asyncio
async def test_bad_command_param(mock_cloud_login_flow_no_local) -> None:  # type:ignore
    """Test bad command parameter handling."""
    username = "user"
    password = "pass"  # noqa: S105

    async with IntelliFireCloudInterface() as cloud_interface:
        await cloud_interface.login_with_credentials(
            username=username, password=password
        )
        user_data = cloud_interface.user_data
        fireplaces = await UnifiedFireplace.build_fireplaces_from_user_data(
            user_data,
            desired_control_mode=IntelliFireApiMode.CLOUD,
            desired_read_mode=IntelliFireApiMode.CLOUD,
        )
        fireplace = fireplaces[0]  # type: ignore #noqa: F841


#
# @pytest.mark.asyncio
# @pytest.mark.parametrize(
#     "status_code, expected_error",
#     [
#         (204, None),  # Success
#         (403, "Not authorized"),
#         (404, "Fireplace not found (bad serial number)"),
#         (422, "Invalid Parameter (invalid command id or command value)"),
#         (69, "Unexpected return code"),
#     ],
# )
# async def test_sending(
#     httpx_mock: HTTPXMock,
#     status_code: int,
#     expected_error: str,
#     enum_fireplaces_json: str,
#     enum_locations_json: str,
#     cloud_poll_json: str,
#     cookies: list[tuple[str, str]],
#     user_id: str,
#     api_key: str,
# ) -> None:
#     """Test some sending."""
#     username = "user"
#     password = "pass"  # noqa: S105
#     httpx_mock.add_response(
#         method="POST",
#         url="https://iftapi.net/a/login",
#         status_code=204,
#         headers=cookies,
#     )
#     httpx_mock.add_response(
#         method="GET",
#         url="https://iftapi.net/a/enumlocations",
#         text=enum_locations_json,
#     )
#
#     httpx_mock.add_response(
#         method="GET",
#         url="https://iftapi.net/a/enumfireplaces?location_id=11118333339267293392",
#         text=enum_fireplaces_json,
#     )
#     httpx_mock.add_response(
#         method="GET",
#         url="https://iftapi.net/a/XXXXXE834CE109D849CBB15CDDBAFF381//apppoll",
#         text=cloud_poll_json,
#     )
#
#     cloud_api = IntelliFireCloudInterface()
#     await cloud_api.login_with_credentials(username=username, password=password)
#     # Fake logged in state
#
#     # cloud_api = IntelliFireAPICloud()
#     # await cloud_api.beep()  # Do nothing
#
#     # ALl this should be mock/patched

#
# @pytest.mark.asyncio
# @pytest.mark.parametrize(
#     "status_code, expected_error",
#     [
#         (204, None),  # Success
#         (403, "Not authorized"),
#         (404, "Fireplace not found (bad serial number)"),
#         (422, "Invalid Parameter (invalid command id or command value)"),
#         (69, "Unexpected return code"),
#     ],
# )
# async def test_sending(
#     status_code: int,
#     expected_error: str,
#     enum_fireplaces_json: str,
#     enum_locations_json: str,
#     cloud_poll_json: str,
#     cookies: list[tuple[str, str]],
#     user_id: str,
#     api_key: str,
# ):
#     """Test some sending."""
#     username = "user"
#     password = "pass"  # noqa: S105
#
#     with aioresponses() as m:
#         # Mocking the POST login request
#         m.post("https://iftapi.net/a/login", status=204, headers=cookies)
#
#         # Mocking other GET requests
#         m.get(
#             "https://iftapi.net/a/enumlocations", status=200, body=enum_locations_json
#         )
#         m.get(
#             "https://iftapi.net/a/enumfireplaces?location_id=11118333339267293392",
#             status=200,
#             body=enum_fireplaces_json,
#         )
#         m.get(
#             "https://iftapi.net/a/XXXXXE834CE109D849CBB15CDDBAFF381//apppoll",
#             status=200,
#             body=cloud_poll_json,
#         )
#
#         async with IntelliFireCloudInterface() as cloud_interface:
#             await cloud_interface.login_with_credentials(
#                 username=username, password=password
#             )
#
#             # Get a fireplace
#             user_data = cloud_interface.user_data
#             fireplaces = await UnifiedFireplace.build_fireplaces_from_user_data(
#                 user_data,
#                 control_mode=IntelliFireApiMode.CLOUD,
#                 read_mode=IntelliFireApiMode.CLOUD,
#             )
#             fireplace = fireplaces[0]
#
#             if expected_error:
#                 with pytest.raises(expected_error):
#                     await fireplace.control_api.beep()
#
#             # Depending on what you are testing, you'll need to simulate sending a request
#             # and mock the response based on the status_code and expected_error parameters
#             # For example, if you're testing a POST request:
#             # m.post("https://iftapi.net/a/some_endpoint", status=status_code)
#
#             # Now you can call the method that sends the request and assert the expected behavior
#             # For example:
#             # if expected_error:
#             #     with pytest.raises(expected_error):
#             #         # Call the method that sends the request
#             #         pass
#             # else:
#             #     # Call the method that sends the request and assert the success case
#             #     pass
#
#
# #
# #
# # async with IntelliFireCloudInterface() as cloud_interface:
# #        await cloud_interface.login_with_credentials(
# #            username=username, password=password
# #        )
# #        user_data = cloud_interface.user_data
# #        fireplaces = await UnifiedFireplace.build_fireplaces_from_user_data(
# #            user_data,
# #            control_mode=IntelliFireApiMode.NONE,
# #            read_mode=IntelliFireApiMode.NONE,
# #        )
# #        fireplace = fireplaces[0]
# #        await fireplace.perform_cloud_poll()
# #        assert fireplace.serial == "XXXXXE834CE109D849CBB15CDDBAFF381"
# #        assert fireplace.data.brand == "H&G"
# #        assert fireplace.data.name == "Living Room"
# #        assert fireplace.api_key == api_key
# #        assert fireplace.data.is_on is False
# #        assert fireplace.data.pilot_on is True
# #
# #        assert cloud_interface.user_data.user_id == user_id
