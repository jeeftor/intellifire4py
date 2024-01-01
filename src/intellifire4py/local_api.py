"""IntelliFire Local API for accessing the fireplace over the lan."""
from __future__ import annotations
import asyncio
import time
from asyncio import Task
from hashlib import sha256
from json import JSONDecodeError
from typing import Any
import logging

from aiohttp import ClientSession, ClientTimeout

from intellifire4py.model import (
    IntelliFirePollData,
)

from .const import IntelliFireCommand
from .const import IntelliFireApiMode
from .control import IntelliFireController
from .read import IntelliFireDataProvider
from .utils import _range_check
import aiohttp


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

        # self._session: ClientSession | None = None

    # async def ensure_session(self) -> None:
    #     """Ensure that the aiohttp ClientSession is created and open."""
    #     if self._session is None or self._session.closed:
    #         self._session = aiohttp.ClientSession(headers={"user-agent": USER_AGENT})
    #
    # async def close_session(self) -> None:
    #     """Close the aiohttp ClientSession."""
    #     if self._session and not self._session.closed:
    #         await self._session.close()

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
            except TimeoutError:
                self.failed_poll_attempts += 1
                self._log.info(
                    "__background_poll:: Polling error [x%d]",
                    self.failed_poll_attempts,
                )

        self._is_polling_in_background = False
        self._log.info("__background_poll:: Background polling disabled.")

    async def poll(
        self, suppress_warnings: bool = False, timeout_seconds: float = 10.0
    ) -> None:
        """Perform a local poll."""

        url = f"http://{self.fireplace_ip}/poll"
        self._log.debug(f"poll() {url} with timeout: {timeout_seconds}")
        try:
            timeout = ClientTimeout(total=timeout_seconds)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                response = await session.get(url)
                response.raise_for_status()  # Handle 4xx/5xx responses here
                try:
                    # Local endpoint doesn't set content_type to JSON
                    json_data = await response.json(content_type=None)
                    self._data = IntelliFirePollData(**json_data)
                    self._log.debug(f"poll() complete: {self._data}")
                except JSONDecodeError as error:
                    if not suppress_warnings:
                        self._log.warning("Error decoding JSON: [%s]", response.text)
                    raise error
        except aiohttp.ClientResponseError as e:
            if e.status == 404 and not suppress_warnings:
                self._log.warning(f"poll() Error accessing {url} - 404")
            raise e
        except asyncio.TimeoutError as error:
            if not suppress_warnings:
                self._log.warning(f"Timeout [{timeout_seconds}] 🕰️ on reading {url} ")
            raise error

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

        async with aiohttp.ClientSession() as session:
            self._log.info(f"Created Client Session {session}")
            # Required fields
            # payload = f"post:command={command.value['local_command']}&value={value}"
            # api_bytes = bytes.fromhex(self._api_key)
            success = False
            while not success:
                # Make a client session
                # async with self._session as client:
                # Await a challenge
                challenge = None
                while not challenge:
                    challenge = await self._get_challenge(session)

                    challenge_time = time.time()
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
                        command=command.value["local_command"],  # type: ignore
                        value=value,
                        challenge=challenge,  # type: ignore
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
                            resp = await session.post(
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
                            if resp.status == 403:
                                self._log.warning(
                                    f"_send_local_command:: : 403 Error - Invalid challenge code (it may have expired): {url}{data}"
                                )
                            if resp.status == 404:
                                self._log.warning(
                                    f"_send_local_command:: Failed to post: {url}{data}"
                                )
                            if resp.status == 422:
                                self._log.warning(
                                    f"_send_local_command:: 422 Code on: {url}{data}"
                                )
                            success = True
                            self._log.debug(
                                "_send_local_command:: Response Code [%d]", resp.status
                            )
                    except asyncio.TimeoutError as error:
                        self._log.warning("Control Endpoint Timeout Error %s", error)
                        continue
                    except Exception as error:
                        self._log.error("Unhandled exception %s", error)
                        self._log.error(error)

                self._log.debug(
                    "_send_local_command:: SUCCESS!! - IntelliFire Command Sent [%s=%s]",
                    command.value["local_command"],
                    value,
                )

    async def _get_challenge(
        self, session: ClientSession
    ) -> str | None:  # due to a bug in typeguard this can't be str | None
        """Retrieve a challenge result from the fireplace."""

        start = time.time()
        try:
            response = await session.get(
                f"http://{self.fireplace_ip}/get_challenge", timeout=3.0
            )
            text = await response.text()
            # text = str(await response.text)
            self._log.info("Received Challenge %s", text)
            return text
        except aiohttp.ClientConnectionError:
            end = time.time()
            self._log.error(
                "time[%.2f] get_challenge returned ClientConnectError",
                (end - start),
            )
            pass
        except asyncio.TimeoutError:
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
