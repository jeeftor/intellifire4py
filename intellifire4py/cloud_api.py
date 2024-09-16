"""IntelliFire CLoud API."""
from __future__ import annotations
import time
import asyncio
from datetime import datetime, timezone

from asyncio import Task
from typing import Any
import json
import aiohttp
from aiohttp import CookieJar, ClientSession, ClientTimeout

from .exceptions import CloudError
from .model import (
    IntelliFireUserData,
)
from .model import IntelliFirePollData

from .const import IntelliFireCommand, IntelliFireApiMode, IntelliFireCloudPollType

from .control import IntelliFireController
from .read import IntelliFireDataProvider
from .utils import _range_check, _convert_aiohttp_response_to_curl
import logging
from .const import USER_AGENT


class IntelliFireAPICloud(IntelliFireController, IntelliFireDataProvider):
    """Api for cloud access."""

    _control_mode = IntelliFireApiMode.CLOUD
    _poll_mode = IntelliFireCloudPollType.LONG

    def __init__(
        self,
        *,
        serial: str,
        use_http: bool = False,
        verify_ssl: bool = True,
        cookie_jar: CookieJar,
    ):
        """Initialize the class with specific configuration for fireplace communication.

        This constructor sets up the class with necessary details for interacting with a fireplace.
        It allows for configuring the communication protocol (HTTP/HTTPS) and SSL verification based
        on the network environment and security requirements. The `use_http` and `verify_ssl` parameters
        are optional and should be modified only in special cases, such as operating within protected networks
        or environments with specific security protocols.

        Args:
            serial (str): Serial number of the fireplace. This is a mandatory parameter used to uniquely
                          identify the fireplace.
            use_http (bool, optional): Whether to use HTTP or HTTPS for communication. Defaults to False,
                          indicating HTTPS is used by default. Set to True to switch to HTTP.
            verify_ssl (bool, optional): Enable or disable SSL certificate verification. Defaults to True,
                          indicating that SSL verification is enabled by default. Set to False to disable
                          verification, which may be necessary in certain network environments with
                          self-signed certificates or lack of SSL support.
            cookie_jar (CookieJar): A `Cookies` object containing authentication or session cookies required for
                          communicating with the fireplace. This is essential for maintaining a secure and
                          authenticated session.

        Note:
            Modifying `use_http` and `verify_ssl` from their default values should be done with caution, as
            it can affect the security and reliability of the communication with the fireplace.
        """
        super(IntelliFireController, self).__init__()
        super(IntelliFireDataProvider, self).__init__()

        self._serial = serial
        self._log = logging.getLogger(__name__)

        self._cookie_jar = cookie_jar

        if use_http:
            self.prefix = "http"  # pragma: no cover
        else:
            self.prefix = "https"
        self._verify_ssl = verify_ssl
        self._is_polling_in_background = False
        self._should_poll_in_background = False
        self._bg_task: Task[Any] | None = None

        # Data is organized by Fireplace Serial Number
        self._data: IntelliFirePollData = IntelliFirePollData()

        # Full data set on the user
        self._user_data: IntelliFireUserData = IntelliFireUserData()

    def _get_session(self, timeout_seconds: float = 10.0) -> ClientSession:
        """Ensure that the aiohttp ClientSession is created and open."""
        timeout = ClientTimeout(timeout_seconds)
        return aiohttp.ClientSession(
            timeout=timeout,
            headers={"user-agent": USER_AGENT},
            cookie_jar=self._cookie_jar,
        )

    def get_data(self) -> IntelliFirePollData:
        """Return data to the user."""
        if (
            self._data.ipv4_address == "127.0.0.1"
        ):  # pragma: no cover - the tests SHOULD be hitting this but dont appear to be
            self._log.warning("Returning uninitialized poll data")  # pragma: no cover
        return self._data

    @property
    def is_polling_in_background(self) -> bool:
        """Return whether api is polling."""
        return self._is_polling_in_background

    async def send_command(self, *, command: IntelliFireCommand, value: int) -> None:
        """Send a command (cloud based)."""
        _range_check(command, value)

        if not self._cookie_jar:
            self._log.warning(
                "Unable to control fireplace with command [%s=%s] Both `api_key` and `user_id` fields must be set.",
                command.name,
                value,
            )
            return

        await self._send_cloud_command(command=command, value=value)

    async def _send_cloud_command(
        self,
        *,
        command: IntelliFireCommand,
        value: int,
    ) -> None:
        url = f"{self.prefix}://iftapi.net/a/{self._serial}//apppost"
        content = f"{command.value['cloud_command']}={value}".encode()

        async with self._get_session().post(url, data=content) as response:
            self._log.info(f">> Created Session {response}")

            curl_command = await _convert_aiohttp_response_to_curl(response)
            self._log.debug(f"Generated curl command: {curl_command}")
            response.raise_for_status()

            log_msg = f"POST {url} [{content.decode()}]  [{self._cookie_jar}]"
            self._log.debug(log_msg)
            """
            204 Success – command accepted
            403 Not authorized (bad email address or authorization cookie)
            404 Fireplace not found (bad serial number)
            422 Invalid Parameter (invalid command id or command value)
            """
            if response.status == 204:
                self._last_send = datetime.now(timezone.utc)
                return
            # elif (
            #     response.status == 403
            # ):  # Not authorized (bad email address or authorization cookie)
            #     raise CloudError("Not authorized")
            # elif response.status == 404:
            #     raise CloudError("Fireplace not found (bad serial number)")
            # elif response.status == 422:
            #     raise CloudError(
            #         "Invalid Parameter (invalid command id or command value)"
            #     )
            else:
                raise Exception(f"Unexpected return code {response.status}")

    async def long_poll(self) -> bool:
        """Perform a LongPoll to wait for a Status update.

        Only returns a status update when the fireplace’s status actually changes (excluding normal periodic
        decreases in the “time remaining” field). If the fireplace status does not change during the time period,
        the server returns status code `408` after the time limit is exceeded. The app can then immediately issue
        another request on this function. If the status changes, then the server returns a `200` status code,
        the status content (in the same format as for apppoll), and an Etag header. The Etag should be sent in an
        If-None- Match header for the next request, so the server knows where in the queue to look for the next
        command to return. The correct order to do this is first issue an apppoll request (or equivalently,
        an enumuserfireplaces request), and then issue applongpoll requests for as long as the status is needed.
        Although this may seem to create a race condition, the server puts fireplace status updates in a queue where
        they last for `30` seconds. Therefore, as long as the Internet connection isn’t unusably slow,
        no status updates will be lost. If the connection goes down, then the process needs to be restarted. The time
        limit is nominally `60` seconds. After `57` seconds, the server will send a `408` response, and after `61` seconds,
        the mobile app should assume that the connection has been dropped.

        Args:
            fireplace (IntelliFireFireplace | None, optional): _description_. Defaults to None.

        Raises:
            ApiCallError: Issue with the API call, either bad credentials or a bad serial number

        Returns:
            bool: `True` if status changed, `False` if it did not
        """

        long_poll_url = f"{self.prefix}://iftapi.net/a/{self._serial}/applongpoll"
        self._log.debug(f"long_poll() {long_poll_url}")

        async with self._get_session() as session:
            try:
                response = await session.get(long_poll_url, timeout=61)

                self._log.debug("Long Poll Status Code %d", response.status)
                if response.status == 200:
                    self._log.debug("Long poll: 200 - Received data")

                    # Data has text/html header type so we need to manually convert it to json
                    json_data = json.loads(await response.text())

                    self._data = IntelliFirePollData(**json_data)
                    self._log.debug(f"poll() complete: {self._data}")

                    self._last_poll = datetime.now(timezone.utc)
                    return True
                elif response.status == 408:
                    self._log.debug("Long poll: 408 - No Data changed")
                    self._last_poll = datetime.now(timezone.utc)
                    return False
            except aiohttp.ClientResponseError as e:
                if e.status == 403:
                    raise CloudError("Not authorized") from e
                if e.status == 404:
                    raise CloudError("Fireplace not found (bad serial number)") from e
                else:
                    response_text = await response.text()
                    self._log.error(
                        f"Unexpected status code: {response.status}, Response: {response_text}"
                    )
                    raise CloudError(
                        f"Unexpected status code: {response.status}"
                    ) from e
        return False

    async def poll(self, timeout_seconds: float = 10.0) -> None:
        """Return a fireplace’s status in JSON.

        Args:
            fireplace (IntelliFireFireplace | None, optional): _description_. Defaults to None.
            timeout_seconds (float): Timeout for the request
        Raises:
            ApiCallError: _description_
            ApiCallError: _description_
            Exception: _description_

        Returns:
            _type_: _description_

        Example:

        .. code-block:: javascript

            {
            "name":"undefined",
            "temperature":"22",
            "battery":"0",
            "pilot":"0",
            "light":"3",
            "height":"4",
            "fanspeed":"0",
            "hot":"0",
            "power":"0",
            "schedule_enable":"0",
            "thermostat":"0",
            "setpoint":"0",
            "timer":"0",
            "timeremaining":"0",
            "prepurge":"0",
            "feature_light":"1",
            "feature_thermostat":"1",
            "power_vent":"0",
            "feature_fan":"1",
            "errors":[3269],
            "firmware_version":"0x01000000"
            "brand":"H&G"
            }

        Errors:
            403: Not Authorized
            404: Bad Serial Number - Fireplace not found

        """

        poll_url = f"{self.prefix}://iftapi.net/a/{self._serial}//apppoll"

        self._log.debug(f"poll() {poll_url}")
        async with self._get_session() as session:
            try:
                response = await session.get(poll_url)
                response.raise_for_status()  # Handle 4xx/5xx responses here
                json_data = await response.json()
                self._data = IntelliFirePollData(**json_data)
                self._log.debug(f"poll() complete: {self._data}")

                self._last_poll = datetime.now(timezone.utc)

            except aiohttp.ClientResponseError as e:
                if e.status == 403:
                    self._log.debug("Not authorized")
                if e.status == 404:
                    self._log.debug("Fireplace not found (bad serial number)")

                # Reraise the exception
                raise e

    async def start_background_polling(self, minimum_wait_in_seconds: int = 10) -> None:
        """Start an ensure-future background polling loop."""

        if not self._should_poll_in_background:
            self._should_poll_in_background = True
            self._log.info("!! start_background_polling !!")

            # Do an initial poll to set data first
            await self.poll()

            self._bg_task = asyncio.create_task(
                self.__background_poll(minimum_wait_in_seconds=minimum_wait_in_seconds),
                name="background_cloud_polling",
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

    async def __background_poll(self, minimum_wait_in_seconds: int = 15) -> None:
        """Start a looping cloud background longpoll task."""
        self._log.debug("__background_poll:: Function Called")
        self._is_polling_in_background = True
        while self._should_poll_in_background:
            start = time.time()
            self._log.debug("__background_poll:: Loop start time %f", start)

            try:
                if self._poll_mode == IntelliFireCloudPollType.LONG:
                    await self.long_poll()
                else:
                    await self.poll()

                #
                # #     has_new_data = await self.long_poll()
                # #
                # #     if new_data:
                # #         self._log.debug(self.data)
                # #
                # # Long poll didn't seem to be working so switched to normal polling again
                #
                # await self.poll()

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
                await asyncio.sleep(minimum_wait_in_seconds - (end - start))
            except Exception as ex:
                self._log.error(ex)
        self._is_polling_in_background = False
        self._log.info("__background_poll:: Background polling disabled.")

    @property
    def data(self) -> IntelliFirePollData:
        """Return data to the user."""
        if (
            self._data.ipv4_address == "127.0.0.1"
        ):  # pragma: no cover - the tests SHOULD be hitting this but dont appear to be
            self._log.warning("Returning uninitialized poll data")  # pragma: no cover
        return self._data

    def set_poll_mode(self, mode: IntelliFireCloudPollType):
        """Set the poll mode."""
        self._poll_mode = mode
