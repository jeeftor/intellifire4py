"""Intellifire Control Logic."""
import asyncio
import os
import time
from types import TracebackType
from typing import List, Optional, Type
import aiohttp

from intellifire4py.const import IntellifireCommand, _log
from intellifire4py.control import LoginException, InputRangeException, ApiCallException
from intellifire4py.model import IntellifireFireplace, IntellifireFireplaces


class AsyncIntellifireControl:
    """Hacked together control API for intellifire modules."""

    def __init__(self, *, fireplace_ip: str) -> None:
        """Init the control class."""
        self._client = aiohttp.ClientSession(raise_for_status=True)
        self._cookie = None
        self.is_logged_in = False
        self._ip = fireplace_ip

    async def close(self) -> None:
        return await self._client.close()

    async def __aenter__(self) -> "Client":
        return self

    async def __aexit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType],
    ) -> Optional[bool]:
        await self.close()
        return None

    async def login(self, *, username: str, password: str) -> None:
        """Run login flow to iftapi.net in order to request cookies."""
        data = f"username={username}&password={password}"

        async with self._client.post("http://iftapi.net/a//login", data=data.encode()) as resp:
            self._cookie = resp.cookies
            self.is_logged_in = True
        return None

    async def _login_check(self) -> None:
        """Check if user is logged in."""
        if not self.is_logged_in:
            raise LoginException("Not Logged In")

    async def get_username(self) -> str:
        """Call to iftapi.net to extract the username based on cookie information."""
        await self._login_check()
        async with self._client.get("http://iftapi.net/a/getusername") as resp:
            ret = await resp.text()
            return ret

    async def get_locations(self) -> List:
        """Enumerate configured locations that a user has access to.

        'location_id' can be used to discovery fireplaces
        and associated serial numbers + api keys at a give location.
        """
        await self._login_check()
        async with self._client.get(url="http://iftapi.net/a/enumlocations") as resp:
            json_data = await resp.json()
            return json_data["locations"]  # type: ignore

    async def get_fireplaces(self, *, location_id: str) -> List[IntellifireFireplace]:
        """Get fireplaces at a location with associated API keys!."""
        await self._login_check()
        async with self._client.get(url=f"http://iftapi.net/a/enumfireplaces?location_id={location_id}") as resp:
            json_data = await resp.json()
            return IntellifireFireplaces(**json_data).fireplaces


    # async def get_challenge(self) -> str:
    #     """Hit the local challenge endpoint."""
    #     async with self._client.get(f"http://{self._ip}/get_challenge") as resp:
    #         ret = resp.text
    #         return ret

    async def _send_cloud_command(self, command: IntellifireCommand, value: int, serial: str) -> None:
        """Send a cloud based control command."""
        await self._login_check()
        data = f"{command.value['value']}={value}"
        async with self._client.post(f"http://iftapi.net/a/{serial}//apppost",data=data.encode()) as resp:
            if resp.status != 204:
                raise ApiCallException("Error with API call")

    async def send_command(
        self,
        *,
        fireplace: IntellifireFireplace,
        command: IntellifireCommand,
        value: int,
    ) -> None:
        """Send a command to a given fireplace."""
        # Validate the range on input
        min_value: int = command.value["min"]  # type: ignore
        max_value: int = command.value["max"]  # type: ignore
        if value > max_value or value < min_value:
            raise InputRangeException(
                field=str(command.value["value"]), min_value=min_value, max_value=max_value
            )
        await self._send_cloud_command(command=command, value=value, serial=fireplace.serial)
        _log.info(f"Sending Intellifire command: [{command.value}={value}]")

    # def _send_local_command(self, command: int) -> None:
    #     """Not yet implemented.
    #
    #     validation code needs to be sent which is sha256(apiKey + sha256(apikey + xxxx + command))
    #     Have been unsure exactly how to encode the data so it matches the sample data I see on charles
    #     """
    #     pass
    #
    async def beep(self, *, fireplace: IntellifireFireplace) -> None:
        """Play a beep - seems to only work if flame is on."""
        await self.send_command(fireplace=fireplace, command=IntellifireCommand.BEEP, value=1)

    async def flame_on(self, *, fireplace: IntellifireFireplace) -> None:
        """Turn on the flame."""
        await self.send_command(
            fireplace=fireplace, command=IntellifireCommand.POWER, value=1
        )

    async def flame_off(self, *, fireplace: IntellifireFireplace) -> None:
        """Turn off the flame."""
        await self.send_command(
            fireplace=fireplace, command=IntellifireCommand.POWER, value=0
        )

    async def set_lights(self, *, fireplace: IntellifireFireplace, level: int) -> None:
        """Modify light levels."""
        await self.send_command(
            fireplace=fireplace, command=IntellifireCommand.LIGHT, value=level
        )

    async def set_flame_height(self, *, fireplace: IntellifireFireplace, height: int) -> None:
        """Set flame height."""
        await self.send_command(
            fireplace=fireplace, command=IntellifireCommand.FLAME_HEIGHT, value=height
        )

    async def set_fan_speed(self, *, fireplace: IntellifireFireplace, speed: int) -> None:
        """Set fan speed."""
        await self.send_command(
            fireplace=fireplace, command=IntellifireCommand.FAN_SPEED, value=speed
        )

    async def fan_off(self, *, fireplace: IntellifireFireplace) -> None:
        """Turn fan off."""
        await self.send_command(
            fireplace=fireplace, command=IntellifireCommand.FAN_SPEED, value=0
        )

    @property
    def user(self) -> str:
        """Get user cookie."""
        return self._cookie.get("user")  # type: ignore

    @property
    def auth_cookie(self) -> str:
        """Get Auth Cookie."""
        return self._cookie.get("auth_cookie")  # type: ignore

    @property
    def web_client_id(self) -> str:
        """Get web client id."""
        return self._cookie.get("web_client_id")  # type: ignore


async def main() -> None:
    """Run main function."""
    username = os.environ["IFT_USER"]
    password = os.environ["IFT_PASS"]

    ift_control = AsyncIntellifireControl(fireplace_ip="192.168.1.65")

    await ift_control.login(username=username, password=password)
    print("Logged in:", ift_control.is_logged_in)

    # Get location list
    locations = await ift_control.get_locations()
    location_id = locations[0]["location_id"]
    print('location_id:', location_id)

    username = await ift_control.get_username()
    print("username", username)

    # Extract a fireplace
    fireplaces = await ift_control.get_fireplaces(
        location_id=location_id
    )
    fireplace: IntellifireFireplace = fireplaces[0]

    sleep_time = 5
    await ift_control.flame_off(fireplace=fireplace)
    time.sleep(sleep_time)
    await ift_control.flame_on(fireplace=fireplace)
    time.sleep(sleep_time)
    await ift_control.set_flame_height(fireplace=fireplace, height=1)
    time.sleep(sleep_time)
    await ift_control.set_flame_height(fireplace=fireplace, height=2)
    time.sleep(sleep_time)
    await ift_control.set_flame_height(fireplace=fireplace, height=3)
    time.sleep(sleep_time)
    await ift_control.set_flame_height(fireplace=fireplace, height=4)
    time.sleep(sleep_time)
    # await ift_control.set_flame_height(fireplace=fireplace, height=5)
    # time.sleep(sleep_time)
    await ift_control.set_flame_height(fireplace=fireplace, height=1)
    time.sleep(sleep_time)
    await ift_control.set_fan_speed(fireplace=fireplace, speed=0)
    time.sleep(sleep_time)
    await ift_control.set_fan_speed(fireplace=fireplace, speed=2)
    time.sleep(sleep_time)
    await ift_control.set_fan_speed(fireplace=fireplace, speed=3)
    time.sleep(sleep_time)
    await ift_control.set_fan_speed(fireplace=fireplace, speed=4)
    time.sleep(sleep_time)
    await ift_control.set_fan_speed(fireplace=fireplace, speed=1)
    time.sleep(sleep_time)
    await ift_control.beep(fireplace=fireplace)
    time.sleep(sleep_time)
    await ift_control.flame_off(fireplace=fireplace)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
