"""IntelliFire Local API for accessing the fireplace over the lan."""
from __future__ import annotations

import asyncio
import time
from asyncio import Task
from hashlib import sha256
from json import JSONDecodeError
from typing import Any
import logging

import httpx
from httpx import ConnectError

from intellifire4py.model import (
    IntelliFirePollData,
)

from .const import IntelliFireCommand
from .const import IntelliFireApiMode
from .control import IntelliFireController
from .read import IntelliFireDataProvider
from .utils import _range_check


class IntelliFireAPILocal(IntelliFireController, IntelliFireDataProvider):
    """Top level API for IntelliFire Data - local network only."""

    _control_mode = IntelliFireApiMode.LOCAL

    # Initialize the global vars
    failed_poll_attempts = 0
    is_sending = False

    def __init__(self, fireplace_ip: str, user_id: str = "", api_key: str = "") -> None:
        """Class Initialization.

        Args:
            fireplace_ip (str): _description_
            user_id (str, optional): The `user_id` as retrieved from :class:`IntelliFireAPICloud`. If left blank - will not be able to control the unit. Defaults to `""`.
            api_key (str, optional): Each fireplace has a unique `api_key`. If left blank - will not be able to control the unit. Defaults to `""`.

        See Also:
            - :func:`IntelliFireAPICloud.login`
            - :func:`IntelliFireAPICloud.get_user_id`
            - :func:`IntelliFireAPICloud.get_fireplace_api_key`

        """
        super(IntelliFireController, self).__init__()
        super(IntelliFireDataProvider, self).__init__()
        self._log = logging.getLogger(__name__)

        self.fireplace_ip = fireplace_ip
        self._api_key = api_key
        self._user_id = user_id
        self._last_thermostat_setpoint: int = 2100
        self.send_mode = IntelliFireApiMode.LOCAL
        self._is_polling_in_background = False
        self._should_poll_in_background = False
        self.is_sending = False
        self.failed_poll_attempts = 0

        self._bg_task: Task[Any] | None = None

        if user_id == "":
            self._log.warning(
                "Instantiating IntelliFireAPILocal without 'user_id' parameter will inhibit the ability to "
                "control the device. "
            )
        if api_key == "":
            self._log.warning(
                "Instantiating IntelliFireAPILocal without 'api_key' parameter will inhibit the ability to "
                "control the device. "
            )

    def log_status(self) -> None:
        """Log a status message."""
        self._log.info(
            "\tIntelliFireAPILocal Status\n\tis_sending\t[%s]\n\tfailed_polls\t[%d]\n\tBG_Running\t[%s]\n\tBG_ShouldRun\t[%s]",
            self.is_sending,
            self.failed_poll_attempts,
            self._is_polling_in_background,
            self._should_poll_in_background,
        )

    def _needs_login(self) -> bool:
        """Return whether a login is required to iftapi.net."""
        return self._api_key == "" or self._user_id == ""

    @property
    def data(self) -> IntelliFirePollData:
        """Return data to the user."""
        if self._data.serial == "unset":
            self._log.warning("Returning uninitialized poll data")
        return self._data

    @property
    def is_polling_in_background(self) -> bool:
        """Return whether api is polling."""
        return self._is_polling_in_background

    async def start_background_polling(self, minimum_wait_in_seconds: int = 15) -> None:
        """Start an ensure-future background polling loop."""
        if self.is_sending:
            self._log.info(
                "!! Suppressing start_background_polling -- sending mode engaged"
            )
            return

        if not self._should_poll_in_background:
            self._should_poll_in_background = True
            self._log.info("!! start_background_polling !!")

            self._bg_task = asyncio.create_task(
                self.__background_poll(minimum_wait_in_seconds),
                name="background_polling",
            )

    async def stop_background_polling(self) -> bool:
        """Stop background polling - return whether it had been polling."""
        self._should_poll_in_background = False
        was_running = False
        if self._bg_task:
            if not self._bg_task.cancelled():
                was_running = True
                self._bg_task.cancel()
                self._log.info("Stopping background task to issue a command")

        return was_running

    async def __background_poll(self, minimum_wait_in_seconds: int = 10) -> None:
        """Perform a polling loop."""
        self._log.debug("__background_poll:: Function Called")

        self.failed_poll_attempts = 0

        self._is_polling_in_background = True
        while self._should_poll_in_background:
            start = time.time()
            self._log.debug("__background_poll:: Loop start time %f", start)

            try:
                await self.poll()
                self.failed_poll_attempts = 0
                end = time.time()

                duration: float = end - start
                sleep_time: float = minimum_wait_in_seconds - duration

                self._log.debug(
                    "__background_poll:: [%f] Sleeping for [%fs]",
                    duration,
                    sleep_time,
                )

                self._log.debug(
                    "__background_poll:: duration: %f, %f, %.2fs",
                    start,
                    end,
                    (end - start),
                )
                self._log.debug(
                    "__background_poll:: Should Sleep For: %f",
                    (minimum_wait_in_seconds - (end - start)),
                )

                await asyncio.sleep(minimum_wait_in_seconds - (end - start))
            except httpx.ReadTimeout:
                self.failed_poll_attempts += 1
                self._log.info(
                    "__background_poll:: Polling error [x%d]",
                    self.failed_poll_attempts,
                )

        self._is_polling_in_background = False
        self._log.info("__background_poll:: Background polling disabled.")

    async def poll(self, suppress_warnings: bool = False) -> None:
        """Read the /poll endpoint.

        Args:
            suppress_warnings (bool, optional): If `True` will inhibit the printing of log messages Useful for a specific case in Home Assistant. Defaults to False.

        Raises:
            ConnectionError: _description_
        """
        url = f"http://{self.fireplace_ip}/poll"
        self._log.debug(f"--IntelliFire:: Querying {url}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                if response.status_code == 404:
                    if not suppress_warnings:
                        # During DHCP Auto discovery may want to suppress error messages
                        self._log.warning(
                            "--IntelliFire:: Error accessing %s - 404", url
                        )
                    raise ConnectionError("Fireplace Endpoint Not Found - 404")
                try:
                    json_data = response.json()
                    self._data = IntelliFirePollData(**json_data)
                except JSONDecodeError:
                    if not suppress_warnings:
                        self._log.warning("Error decoding JSON: [%s]", response.text)
                except httpx.ReadTimeout:
                    if not suppress_warnings:
                        self._log.warning("Timeout error on polling")
        except httpx.ReadTimeout:
            self._log.warning(f"Timeout on reading {url}")
        except ConnectError as err:
            raise ConnectionError from err

    async def send_command(
        self,
        *,
        command: IntelliFireCommand,
        value: int,
    ) -> None:
        """Send a command (local only for now)."""
        _range_check(command, value)

        if self._needs_login():
            self._log.warning(
                "Unable to control fireplace with command [%s=%s] Both `api_key` and `user_id` fields must be set.",
                command.name,
                value,
            )
            return

        was_running = await self.stop_background_polling()
        self._log.debug(
            "send_command:: Stopped background task which was running? [%s]",
            was_running,
        )

        await self._send_local_command(command=command, value=value)

        if was_running:
            await self.start_background_polling()
            self._log.info("send_command:: Restarting background polling")

    def _construct_payload(self, command: str, value: int, challenge: str) -> str:
        """Construct a payload."""
        payload = f"post:command={command}&value={value}"
        api_bytes = bytes.fromhex(self._api_key)
        challenge_bytes = bytes.fromhex(challenge)
        payload_bytes = payload.encode()
        response = sha256(
            api_bytes + sha256(api_bytes + challenge_bytes + payload_bytes).digest()
        ).hexdigest()
        return (
            f"command={command}&value={value}&user={self._user_id}&response={response}"
        )

    async def _send_local_command(
        self,
        *,
        command: IntelliFireCommand,
        value: int,
    ) -> None:
        """Send a local command to the /post interface."""
        # Required fields
        # payload = f"post:command={command.value['local_command']}&value={value}"
        # api_bytes = bytes.fromhex(self._api_key)
        success = False
        while not success:
            # Make a client session
            async with httpx.AsyncClient() as client:
                # Await a challenge
                challenge = None
                while not challenge:
                    challenge = await self._get_challenge(client)

                challenge_time = time.time()  # type: ignore
                #
                # challenge_bytes = bytes.fromhex(challenge)
                # payload_bytes = payload.encode()
                #
                # response = sha256(
                #     api_bytes
                #     + sha256(api_bytes + challenge_bytes + payload_bytes).digest()
                # ).hexdigest()

                # data = f"command={command.value['local_command']}&value={value}&user={self._user_id}&response={response}"
                data = self._construct_payload(
                    command=command.value["local_command"],
                    value=value,
                    challenge=challenge,
                )
                url = f"http://{self.fireplace_ip}/post"
                try:
                    while (time.time() - challenge_time) < 5 and not success:
                        # There is a 10 second timeout on the challenge response - we'll try for 5
                        self._log.info(
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
                            timeout=1.0,
                        )
                        self._log.debug(
                            "_send_local_command:: Sending Local IntelliFire command: [%s=%s]",
                            command.value["local_command"],
                            value,
                        )
                        if resp.status_code == 403:
                            self._log.warning(
                                f"_send_local_command:: : 403 Error - Invalid challenge code (it may have expired): {url}{data}"
                            )
                        if resp.status_code == 404:
                            self._log.warning(
                                f"_send_local_command:: Failed to post: {url}{data}"
                            )
                        if resp.status_code == 422:
                            self._log.warning(
                                f"_send_local_command:: 422 Code on: {url}{data}"
                            )
                        success = True
                        self._log.debug(
                            "_send_local_command:: Response Code [%d]", resp.status_code
                        )
                # except ClientResponseError:
                #     self._log.debug(
                #         "_send_local_command: 403 Error - Invalid challenge code (it may have expired) "
                #     )
                #     continue
                except httpx.ReadTimeout as error:
                    self._log.warning("Control Endpoint Timeout Error %s", error)
                    continue
                except Exception as error:
                    self._log.error("Unhandled exception %s", error)
                    self._log.error(error)

            self._log.debug(  # type: ignore
                "_send_local_command:: SUCCESS!! - IntelliFire Command Sent [%s=%s]",
                command.value["local_command"],
                value,
            )

    async def _get_challenge(
        self, client: httpx.AsyncClient
    ) -> str | None:  # due to a bug in typeguard this can't be str | None
        """Retrieve a challenge result from the fireplace."""
        start = time.time()
        try:
            response = await client.get(
                f"http://{self.fireplace_ip}/get_challenge", timeout=3.0
            )
            text = response.text
            # text = str(await response.text)
            self._log.info("Received Challenge %s", text)
            return text
        except httpx.ConnectError:
            end = time.time()
            self._log.error(
                "time[%.2f] get_challenge returned ClientConnectError",
                (end - start),
            )
            pass
        except (httpx.ReadTimeout, TimeoutError, asyncio.exceptions.TimeoutError):
            end = time.time()
            self._log.warning(
                "time[%.2f] get_challenge returned TimeoutError", (end - start)
            )
            pass
        except Exception as error:
            end = time.time()
            self._log.error(
                "time[%.2f] get_challenge returned exception [%s]",
                (end - start),
                str(type(error)),
            )

        await asyncio.sleep(1)
        return None

    #
    # async def flame_on(self) -> None:
    #     """Turn on the flame."""
    #     await self.send_command(command=IntelliFireCommand.POWER, value=1)
    #     self._data.is_on = True
    #
    # async def flame_off(self) -> None:
    #     """Turn off the flame."""
    #     await self.send_command(command=IntelliFireCommand.POWER, value=0)
    #     self._data.is_on = False
    #
    # async def pilot_on(self) -> None:
    #     """Turn on the pilot light."""
    #     await self.send_command(command=IntelliFireCommand.PILOT, value=1)
    #     self._data.pilot_on = True
    #
    # async def pilot_off(self) -> None:
    #     """Turn off the pilot light."""
    #     await self.send_command(command=IntelliFireCommand.PILOT, value=0)
    #     self._data.pilot_on = False
    #
    # async def set_lights(self, level: int) -> None:
    #     """Modify light levels."""
    #     await self.send_command(command=IntelliFireCommand.LIGHT, value=level)
    #     self._data.light_level = level
    #
    # async def set_flame_height(self, height: int) -> None:
    #     """Set flame height.
    #
    #     Args:
    #         height (int): Valid height `0`-`4` (in the future this will be 1-5)
    #     """
    #     await self.send_command(command=IntelliFireCommand.FLAME_HEIGHT, value=height)
    #     self._data.flameheight = height
    #
    # async def set_fan_speed(self, speed: int) -> None:
    #     """Set fan speed."""
    #     await self.send_command(command=IntelliFireCommand.FAN_SPEED, value=speed)
    #     self._data.fanspeed = speed
    #
    # async def fan_off(self) -> None:
    #     """Turn fan off."""
    #     await self.set_fan_speed(speed=0)
    #
    # async def turn_off_thermostat(self) -> None:
    #     """Turn off thermostat mode."""
    #     await self.send_command(command=IntelliFireCommand.THERMOSTAT_SETPOINT, value=0)
    #     self._data.raw_thermostat_setpoint = 0
    #
    # async def turn_on_thermostat(self) -> None:
    #     """Turn on thermostat mode."""
    #     await self.send_command(
    #         command=IntelliFireCommand.THERMOSTAT_SETPOINT,
    #         value=self._last_thermostat_setpoint,
    #     )
    #     self._data.raw_thermostat_setpoint = self._last_thermostat_setpoint * 100
    #
    # async def set_thermostat_f(self, temp_f: int) -> None:
    #     """Set thermostat value in fahrenheit.
    #
    #     Example:
    #
    #         .. code:: Python
    #
    #             # Set to 70 and store the value internally
    #             await ift_control.set_thermostat_f(temp_f=70)
    #             # Turn off thermostat
    #             await ift_control.turn_off_thermostat()
    #             # Turn on thermostat - will remember the last temp (70)
    #             await ift_control.turn_on_thermostat()
    #     """
    #
    #     temp_c = int((temp_f - 32) * 5 / 9)
    #     await self.set_thermostat_c(temp_c=(temp_c))
    #
    # async def set_thermostat_c(self, temp_c: int) -> None:
    #     """Set thermostat value in centigrade."""
    #     self._last_thermostat_setpoint = temp_c
    #     # Need to multiply actual c value by 100 to meet
    #     # api specs. Not sure why :)
    #     await self.send_command(
    #         command=IntelliFireCommand.THERMOSTAT_SETPOINT,
    #         value=temp_c * 100,
    #     )
    #     self._data.raw_thermostat_setpoint = temp_c * 100
    #
    # async def set_sleep_timer(self, minutes: int) -> None:
    #     """Set the sleep timer in minutes.
    #
    #     Args:
    #         minutes (int): Valid range `0`-`180`
    #     """
    #     await self.send_command(
    #         command=IntelliFireCommand.TIME_REMAINING,
    #         value=minutes * 60,  # api requires seconds - but we will work in minutes
    #     )
    #     self._data.timeremaining_s = 60 * minutes
    #
    # async def stop_sleep_timer(self) -> None:
    #     """Stop the sleep timer."""
    #     await self.send_command(command=IntelliFireCommand.TIME_REMAINING, value=0)
    #     self._data.timer_on = False
    #     self._data.timeremaining_s = 0
