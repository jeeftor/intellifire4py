"""IntelliFire CLoud API."""
from __future__ import annotations

import httpx
from httpx import Cookies

from intellifire4py.exceptions import LoginError
from intellifire4py.model import IntelliFireFireplace
from intellifire4py.model import IntelliFireFireplaces

from .const import _log


class IntelliFireAPICloud:
    """Api for cloud access."""

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

    def p2(self):
        """Set thermostat value in fahrenheit.

        .. code:: javascript

            { key : value,
              key2: value,
              }
        """

    def poll(self):
        """Returns a fireplace’s status in JSON.

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
        pass
