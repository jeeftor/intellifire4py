"""IntelliFire CLoud API."""
from __future__ import annotations

import asyncio

import httpx
from httpx import Cookies
from asyncio import Task
from typing import Any
import time

from intellifire4py.exceptions import ApiCallError
from intellifire4py.exceptions import LoginError
from intellifire4py.model import IntelliFireFireplace
from intellifire4py.model import IntelliFireFireplaces
from intellifire4py.model import IntelliFirePollData

from .const import IntelliFireCommand
from .const import _log
from .control import IntelliFireController, IntelliFireControlMode
from .utils import _range_check


class IntelliFireAPICloud(IntelliFireController):
    """Api for cloud access."""

    _control_mode = IntelliFireControlMode.CLOUD

    def __init__(self, *, use_http: bool = False, verify_ssl: bool = True):
        """Initialize the class.

        In most cases you should not specify either the `use_http` or `verify_ssl` parameters - however in some special cases such as protected networks you may need these options.

        Args:
            use_http (bool, optional): whether to use HTTP or HTTPS mode. Defaults to False.
            verify_ssl (bool, optional): Enable/Disable SSL Verification. Defaults to True.
        """
        self._cookie: Cookies = Cookies()
        self._is_logged_in = False
        self.default_fireplace: IntelliFireFireplace
        if use_http:
            self.prefix = "http"
        else:
            self.prefix = "https"
        self._verify_ssl = verify_ssl
        self.is_polling_in_background = False
        self._should_poll_in_background = False
        self._bg_task: Task[Any] | None = None

    @property
    def data(self) -> IntelliFirePollData:
        """Return data to the user."""
        if self._data.serial == "unset":
            _log.warning("Returning uninitialized poll data")
        return self._data

    async def login(self, *, username: str, password: str) -> None:
        """Login to Cloud API.

        Args:
            username (str): IFTAPI.net Username (usually email)
            password (str): IFTAPI.net Password

        Raises:
            LoginError: _description_

        Returns:
            None

        """
        data = {"username": username, "password": password}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.prefix}://iftapi.net/a/login",
                    data=data,  # .encode(),
                )

                if response.status_code != 204:
                    raise LoginError()

                self._cookie = response.cookies
                _log.debug(response.cookies)
                self._is_logged_in = True
                _log.info("Success - Logged into IFTAPI")

                # Now set the default fireplace
                await self._set_default_fireplace(client)

            except LoginError as ex:
                _log.warning("Login failure")
                raise ex
            return None

    async def _set_default_fireplace(self, client: httpx.AsyncClient) -> None:
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

    async def get_locations(self, client: httpx.AsyncClient) -> list[dict[str, str]]:
        """Enumerate configured locations that a user has access to.

        'location_id' can be used to discovery fireplaces
        and associated serial numbers + api keys at a give location.
        """
        await self._login_check()
        response = await client.get(url=f"{self.prefix}://iftapi.net/a/enumlocations")
        json_data = response.json()
        locations: list[dict[str, str]] = json_data["locations"]
        return locations

    async def get_fireplaces(
        self, client: httpx.AsyncClient, *, location_id: str
    ) -> list[IntelliFireFireplace]:
        """Get fireplaces at a location with associated API keys!."""
        await self._login_check()
        response = await client.get(
            url=f"{self.prefix}://iftapi.net/a/enumfireplaces?location_id={location_id}"
        )
        json_data = response.json()
        _log.debug(json_data)
        return IntelliFireFireplaces(**json_data).fireplaces

    async def _login_check(self) -> None:
        """Check if user is logged in."""
        if not self._is_logged_in:
            raise LoginError("Not Logged In")

    def get_user_id(self) -> str:
        """Get user ID from cloud."""
        user_id = str(self._cookie.get("user"))
        return user_id

    def get_fireplace_api_key(
        self, fireplace: IntelliFireFireplace | None = None
    ) -> str:
        """Get API key for specific fireplace."""
        if not fireplace:
            return self.default_fireplace.apikey
        return fireplace.apikey

    async def send_command(
        self,
        *,
        command: IntelliFireCommand,
        value: int,
    ) -> None:
        """Send a command (cloud based)."""
        _range_check(command, value)

        if not self._is_logged_in:
            _log.warning(
                "Unable to control fireplace with command [%s=%s] Both `api_key` and `user_id` fields must be set.",
                command.name,
                value,
            )
            return

        await self._send_cloud_command(command=command, value=value)

    async def _send_cloud_command(
        self,
        fireplace: IntelliFireFireplace | None = None,
        *,
        command: IntelliFireCommand,
        value: int,
    ) -> None:
        async with httpx.AsyncClient(cookies=self._cookie) as client:
            if not fireplace:
                serial = self.default_fireplace.serial
            else:
                serial = fireplace.serial

            # Construct body
            content = f"{command.value['cloud_command']}={value}".encode()
            response = await client.post(
                f"{self.prefix}://iftapi.net/a/{serial}/apppost", content=content
            )
            """
            204 Success – command accepted
            403 Not authorized (bad email address or authorization cookie)
            404 Fireplace not found (bad serial number)
            422 Invalid Parameter (invalid command id or command value)
            """
            if response.status_code == 204:
                return
            elif (
                response.status_code == 403
            ):  # Not authorized (bad email address or authorization cookie)
                raise ApiCallError("Not authorized")
            elif response.status_code == 404:
                raise ApiCallError("Fireplace not found (bad serial number)")
            elif response.status_code == 422:
                raise ApiCallError(
                    "Invalid Parameter (invalid command id or command value)"
                )
            else:
                raise Exception("Unexpected return code")

    async def long_poll(self, fireplace: IntelliFireFireplace | None = None) -> bool:
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

        await self._login_check()
        async with httpx.AsyncClient(cookies=self._cookie, timeout=61) as client:
            if not fireplace:
                serial = self.default_fireplace.serial
            else:
                serial = fireplace.serial
            response = await client.get(
                f"{self.prefix}://iftapi.net/a/{serial}/applongpoll"
            )
            if response.status_code == 200:
                return True
            elif response.status_code == 408:
                _log.debug("Long Poll returned 408 - no data changed")
                return False
            elif (
                response.status_code == 403
            ):  # Not authorized (bad email address or authorization cookie)
                raise ApiCallError("Not authorized")
            elif response.status_code == 404:
                raise ApiCallError("Fireplace not found (bad serial number)")
            else:
                raise Exception("Unexpected return code")

    async def poll(self, fireplace: IntelliFireFireplace | None = None) -> None:
        """Return a fireplace’s status in JSON.

        Args:
            fireplace (IntelliFireFireplace | None, optional): _description_. Defaults to None.

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

        """
        await self._login_check()
        async with httpx.AsyncClient(cookies=self._cookie) as client:
            if not fireplace:
                serial = self.default_fireplace.serial
            else:
                serial = fireplace.serial
            response = await client.get(
                f"{self.prefix}://iftapi.net/a/{serial}//apppoll"
            )
            if response.status_code == 200:
                json_data = response.json()
                self._data: IntelliFirePollData = IntelliFirePollData(**json_data)

            elif (
                response.status_code == 403
            ):  # Not authorized (bad email address or authorization cookie)
                raise ApiCallError("Not authorized")
            elif response.status_code == 404:
                raise ApiCallError("Fireplace not found (bad serial number)")
            else:
                raise Exception("Unexpected return code")

    async def start_background_polling(self) -> None:
        """Start an ensure-future background polling loop."""

        if not self._should_poll_in_background:
            self._should_poll_in_background = True
            _log.info("!!  start_background_polling !!")

            self._bg_task = asyncio.create_task(
                self.__background_poll(), name="background_cloud_polling"
            )

    def stop_background_polling(self) -> bool:
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
        """Start a looping background longpoll task."""
        _log.debug("__background_poll:: Function Called")
        self.is_polling_in_background = True
        while self._should_poll_in_background:
            start = time.time()
            _log.debug("__background_poll:: Loop start time %f", start)

            try:
                new_data = await self.long_poll()
                if new_data:
                    _log.debug(self.data)

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
                await asyncio.sleep(minimum_wait_in_seconds - (end - start))
            except Exception as ex:
                _log.error(ex)
        self.is_polling_in_background = False
        _log.info("__background_poll:: Background polling disabled.")
