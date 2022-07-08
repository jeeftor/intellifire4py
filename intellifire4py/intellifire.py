"""Unified intellifire API."""
from __future__ import annotations

import asyncio
import time
from asyncio import Task
from hashlib import sha256
from json import JSONDecodeError

import aiohttp
from aiohttp import (
    ClientConnectorError,
    ClientOSError,
    ClientResponseError,
    ClientSession,
    ServerDisconnectedError,
)

from intellifire4py.exceptions import InputRangeException, LoginException
from intellifire4py.model import (
    IntellifireFireplace,
    IntellifireFireplaces,
    IntellifirePollData,
)

from .const import IntellifireCommand, _log
from .control_async import IntellifireSendMode


class IntellifireAPILocal:
    """Top level API for Intellifire Data - local network only."""

    # Initialize the global vars
    failed_poll_attempts = 0
    is_sending = False

    def __init__(self, fireplace_ip: str, user_id: str = "", api_key: str = "") -> None:
        """Initialize Intellifire Class."""
        self._data = IntellifirePollData()
        self.fireplace_ip = fireplace_ip
        self._api_key = api_key
        self._user_id = user_id
        self._last_thermostat_setpoint: int = 2100
        self.send_mode = IntellifireSendMode.LOCAL

        self.is_polling_in_background = False
        self._should_poll_in_background = False
        self.is_sending = False
        self.failed_poll_attempts = 0

        self._bg_task: Task | None = None

    def log_status(self) -> None:
        """Log a status message."""
        _log.info(
            "\tIntellifireAPILocal Status\n\tis_sending\t[%s]\n\tfailed_polls\t[%d]\n\tBG_Running\t[%s]\n\tBG_ShouldRun\t[%s]",
            self.is_sending,
            self.failed_poll_attempts,
            self.is_polling_in_background,
            self._should_poll_in_background,
        )

    def _needs_login(self) -> bool:
        """Return whether a login is required to iftapi.net."""
        return self._api_key == "" or self._user_id == ""

    @property
    def data(self) -> IntellifirePollData:
        """Return data to the user."""
        if self._data.serial == "unset":
            _log.warning("Returning uninitialized poll data")
        return self._data

    async def start_background_polling(self, minimum_wait_in_seconds: int = 15) -> None:
        """Start an ensure-future background polling loop."""
        if self.is_sending:
            _log.info("!! Suppressing start_background_polling -- sending mode engaged")
            return

        if not self._should_poll_in_background:
            self._should_poll_in_background = True
            # asyncio.ensure_future(self.__background_poll(minimum_wait_in_seconds))
            _log.info("!!  start_background_polling !!")

            self._bg_task = asyncio.create_task(
                self.__background_poll(minimum_wait_in_seconds),
                name="background_polling",
            )

    def stop_background_polling(self, is_sending: bool) -> bool:
        """Stop background polling - return whether it had been polling."""
        self._should_poll_in_background = False
        was_running = False
        if self._bg_task:
            if not self._bg_task.cancelled():
                was_running = True
                self._bg_task.cancel()
                _log.info("Stopping background task to issue a command")

        return was_running

    async def __background_poll(self, minimum_wait_in_seconds: int = 10) -> None:
        """Perform a polling loop."""
        _log.debug("__background_poll:: Function Called")

        self.failed_poll_attempts = 0

        self.is_polling_in_background = True
        while self._should_poll_in_background:

            start = time.time()
            _log.debug("__background_poll:: Loop start time %f", start)

            try:
                await self.poll()
                self.failed_poll_attempts = 0
                end = time.time()

                duration: float = end - start
                sleep_time: float = minimum_wait_in_seconds - duration

                _log.debug(
                    "__background_poll:: [%f] Sleeping for [%fs]", duration, sleep_time
                )

                _log.debug(
                    "__background_poll:: duration: %f, %f, %.2fs",
                    start,
                    end,
                    (end - start),
                )
                _log.debug(
                    "__background_poll:: Should Sleep For: %f",
                    (minimum_wait_in_seconds - (end - start)),
                )

                await asyncio.sleep(minimum_wait_in_seconds - (end - start))
            except (ConnectionError, ClientOSError):
                self.failed_poll_attempts += 1
                _log.info(
                    "__background_poll:: Polling error [x%d]", self.failed_poll_attempts
                )

        self.is_polling_in_background = False
        _log.info("__background_poll:: Background polling disabled.")

    async def poll(self, suppress_warnings: bool = False) -> None:
        """Poll the IFT module locally."""
        async with aiohttp.ClientSession() as session:
            url = f"http://{self.fireplace_ip}/poll"

            _log.debug(f"--Intellifire:: Querying {url}")
            try:
                async with session.get(url) as response:

                    try:
                        if response.status == 404:
                            # Valid address - but poll endpoint not found

                            if not suppress_warnings:
                                # During DHCP Auto discovery may want to suppress error messages
                                _log.warning(
                                    "--Intellifire:: Error accessing %s - 404", url
                                )
                            raise ConnectionError("Fireplace Endpoint Not Found - 404")
                        try:
                            json_data = await response.json(content_type=None)
                            _log.debug("Received: %s", json_data)
                        except JSONDecodeError:
                            if not suppress_warnings:
                                _log.warning("Error decoding JSON: [%s]", response.text)

                        _log.debug("Updating self._data")
                        self._data = IntellifirePollData(**json_data)
                    except ConnectionError:
                        if not suppress_warnings:
                            _log.warning("Connection Error accessing", url)
                        raise ConnectionError("ConnectionError - host not found")
            except (
                ServerDisconnectedError,
                ClientConnectorError,
                ClientOSError,
                ConnectionError,
                UnboundLocalError,
            ):
                raise ConnectionError()
            except Exception as unknown_error:
                _log.error("Unhandled Exception %s", type(unknown_error))

    async def send_command(
        self,
        *,
        command: IntellifireCommand,
        value: int,
    ) -> None:
        """Send a command (local only for now)."""
        # Validate the range on input
        min_value: int = command.value["min"]  # type: ignore
        max_value: int = command.value["max"]  # type: ignore

        if value > max_value or value < min_value:
            raise InputRangeException(
                field=str(command.name),
                min_value=min_value,
                max_value=max_value,
            )

        was_running = self.stop_background_polling(is_sending=True)
        _log.debug(
            "send_command:: Stopped background task which was running? [%s]",
            was_running,
        )

        # async with aiohttp.ClientSession() as client:
        await self._send_local_command(command=command, value=value)

        if was_running:
            await self.start_background_polling()
            _log.info("send_command:: Restarting background polling")

    async def _send_local_command(
        self,
        *,
        command: IntellifireCommand,
        value: int,
    ) -> None:
        """Send a local command to the /post interface."""

        # Required fields
        payload = f"post:command={command.value['local_command']}&value={value}"
        api_bytes = bytes.fromhex(self._api_key)
        success = False
        while not success:

            # Make a client session
            async with aiohttp.ClientSession() as client:

                # Await a challenge
                challenge = None
                while not challenge:
                    challenge = await self._get_challenge(client)

                challenge_time = time.time()

                challenge_bytes = bytes.fromhex(challenge)
                payload_bytes = payload.encode()

                response = sha256(
                    api_bytes
                    + sha256(api_bytes + challenge_bytes + payload_bytes).digest()
                ).hexdigest()

                data = f"command={command.value['local_command']}&value={value}&user={self._user_id}&response={response}"
                url = f"http://{self.fireplace_ip}/post"
                try:
                    while (time.time() - challenge_time) < 5 and not success:
                        # There is a 10 second timeout on the challenge response - we'll try for 5
                        _log.info(
                            "_send_local_command:: -- Attempting command via post %d [%s]",
                            (time.time() - challenge_time),
                            challenge,
                        )
                        await asyncio.sleep(1)
                        resp = await client.post(
                            url=url,
                            data=data,
                            headers={
                                "content-type": "application/x-www-form-urlencoded"
                            },
                            timeout=aiohttp.ClientTimeout(total=1),
                            raise_for_status=True,
                        )
                        _log.debug(
                            "_send_local_command:: Sending Local Intellifire command: [%s=%s]",
                            command.value["local_command"],
                            value,
                        )

                        if resp.status == 404:
                            _log.warning(
                                f"_send_local_command:: Failed to post: {url}{data}"
                            )
                        if resp.status == 422:
                            _log.warning(
                                f"_send_local_command:: 422 Code on: {url}{data}"
                            )
                        success = True
                        _log.debug(
                            "_send_local_command:: Response Code [%d]", resp.status
                        )
                except ClientResponseError:
                    _log.debug(
                        "_send_local_command: 403 Error - Invalid challenge code (it may have expired) "
                    )
                    continue
                except Exception as error:
                    _log.error(error)

            _log.debug(
                "_send_local_command:: SUCCESS!! - Intellifire Command Sent [%s=%s]",
                command.value["local_command"],
                value,
            )  # Unreachable -- no error

    async def _get_challenge(self, client: ClientSession) -> str | None:
        """Retrieve a challenge result from the fireplace."""
        start = time.time()
        try:
            resp = await client.get(
                f"http://{self.fireplace_ip}/get_challenge",
                timeout=aiohttp.ClientTimeout(total=3),
            )
            text = str(await resp.text())
            _log.info("Received Challenge %s", text)
            return text
        except ClientConnectorError:
            end = time.time()
            _log.error(
                "time[%.2f] get_challenge returned ClientConnectError",
                (end - start),
            )
            pass
        except (TimeoutError, asyncio.exceptions.TimeoutError):
            end = time.time()
            _log.error("time[%.2f] get_challenge returned TimeoutError", (end - start))
            pass
        except Exception as error:
            end = time.time()
            _log.error(
                "time[%.2f] get_challenge returned exception [%s]",
                (end - start),
                str(type(error)),
            )

        await asyncio.sleep(1)
        return None

    async def flame_on(self) -> None:
        """Turn on the flame."""
        await self.send_command(command=IntellifireCommand.POWER, value=1)
        self._data.is_on = True

    async def flame_off(self) -> None:
        """Turn off the flame."""
        await self.send_command(command=IntellifireCommand.POWER, value=0)
        self._data.is_on = False

    async def pilot_on(self) -> None:
        """Turn on the pilot light."""
        await self.send_command(command=IntellifireCommand.PILOT, value=1)
        self._data.pilot_on = True

    async def pilot_off(self) -> None:
        """Turn off the pilot light."""
        await self.send_command(command=IntellifireCommand.PILOT, value=0)
        self._data.pilot_on = False

    async def set_lights(self, level: int) -> None:
        """Modify light levels."""
        await self.send_command(command=IntellifireCommand.LIGHT, value=level)
        self._data.light_level = level

    async def set_flame_height(self, height: int) -> None:
        """Set flame height."""
        await self.send_command(command=IntellifireCommand.FLAME_HEIGHT, value=height)
        self._data.flameheight = height

    async def set_fan_speed(self, speed: int) -> None:
        """Set fan speed."""
        await self.send_command(command=IntellifireCommand.FAN_SPEED, value=speed)
        self._data.fanspeed = speed

    async def fan_off(self) -> None:
        """Turn fan off."""
        await self.set_fan_speed(speed=0)

    async def turn_off_thermostat(self) -> None:
        """Turn off thermostat mode."""
        await self.send_command(command=IntellifireCommand.THERMOSTAT_SETPOINT, value=0)
        self._data.raw_thermostat_setpoint = 0

    async def turn_on_thermostat(self) -> None:
        """Turn on thermostat mode."""
        await self.send_command(
            command=IntellifireCommand.THERMOSTAT_SETPOINT,
            value=self._last_thermostat_setpoint,
        )
        self._data.raw_thermostat_setpoint = self._last_thermostat_setpoint * 100

    async def set_thermostat_f(self, temp_f: int) -> None:
        """Set thermostat value in fahrenheit."""
        temp_c = int((temp_f - 32) * 5 / 9)
        await self.set_thermostat_c(temp_c=(temp_c))

    async def set_thermostat_c(self, temp_c: int) -> None:
        """Set thermostat value in centigrade."""
        self._last_thermostat_setpoint = temp_c
        # Need to multiply actual c value by 100 to meet
        # api specs. Not sure why :)
        await self.send_command(
            command=IntellifireCommand.THERMOSTAT_SETPOINT,
            value=temp_c * 100,
        )
        self._data.raw_thermostat_setpoint = temp_c * 100

    async def set_sleep_timer(self, minutes: int) -> None:
        """Set the sleep timer in minutes."""
        await self.send_command(
            command=IntellifireCommand.TIME_REMAINING,
            value=minutes * 60,  # api requires seconds - but we will work in minutes
        )
        self._data.timeremaining_s = 60 * minutes

    async def stop_sleep_timer(self) -> None:
        """Stop the sleep timer."""
        await self.send_command(command=IntellifireCommand.TIME_REMAINING, value=0)
        self._data.timer_on = False
        self._data.timeremaining_s = 0


class IntellifireAPICloud:
    """Api for cloud access."""

    def __init__(self, *, use_http: bool = False, verify_ssl: bool = True):
        """Instantiate cloud api."""
        self._cookie = None
        self._is_logged_in = False
        self.default_fireplace: IntellifireFireplace
        if use_http:
            self.prefix = "http"
        else:
            self.prefix = "https"
        self._verify_ssl = verify_ssl

    async def login(self, *, username: str, password: str) -> None:
        """Login to iftapi.net."""
        data = f"username={username}&password={password}"

        async with aiohttp.ClientSession() as client:
            try:
                async with client.post(
                    f"{self.prefix}://iftapi.net/a//login",
                    data=data.encode(),
                    ssl=False,
                ) as response:

                    if response.status != 204:
                        raise LoginException()

                    self._cookie = response.cookies
                    self.is_logged_in = True
                    _log.info("Success - Logged into IFTAPI")

                    # Now set the default fireplace
                    await self._set_default_fireplace(client)

            except LoginException as ex:
                _log.warning("Login failure")
                raise ex
            return None

    async def _set_default_fireplace(self, client: aiohttp.ClientSession) -> None:
        """Set default_fireplace value assuming 1 fireplace and 1 location.

        This function will call get_locations and get_fireplaces in order to preset the default fireplace value.
        This will probably cover most home installs where people only have a single IFT fireplace.
        """
        locations = await self.get_locations(client=client)
        fireplaces = await self.get_fireplaces(
            client=client, location_id=locations[0]["location_id"]
        )
        self.default_fireplace = fireplaces[0]
        _log.debug(f"configure default fireplace: {self.default_fireplace.serial}")

    async def get_locations(self, client: aiohttp.ClientSession) -> list:
        """Enumerate configured locations that a user has access to.

        'location_id' can be used to discovery fireplaces
        and associated serial numbers + api keys at a give location.
        """
        await self._login_check()
        async with client.get(
            url=f"{self.prefix}://iftapi.net/a/enumlocations"
        ) as resp:
            json_data = await resp.json()
            return json_data["locations"]  # type: ignore

    async def get_fireplaces(
        self, client: aiohttp.ClientSession, *, location_id: str
    ) -> list[IntellifireFireplace]:
        """Get fireplaces at a location with associated API keys!."""
        await self._login_check()
        async with client.get(
            url=f"{self.prefix}://iftapi.net/a/enumfireplaces?location_id={location_id}"
        ) as resp:
            json_data = await resp.json()
            return IntellifireFireplaces(**json_data).fireplaces

    async def _login_check(self) -> None:
        """Check if user is logged in."""

        if not self.is_logged_in:
            raise LoginException("Not Logged In")

    def get_user_id(self) -> str:
        """Get user ID from cloud."""
        user_id = str(self._cookie.get("user").value)  # type: ignore
        if isinstance(user_id, (list, tuple)):
            return user_id[0]
        return user_id

        return

    def get_fireplace_api_key(
        self, fireplace: IntellifireFireplace | None = None
    ) -> str:
        """Get API key for specific fireplace."""
        if not fireplace:
            return self.default_fireplace.apikey

        if isinstance(fireplace.apikey, (list, tuple)):
            return fireplace.apikey[0]
        return fireplace.apikey
