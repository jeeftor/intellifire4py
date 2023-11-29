"""Main API access to the Cloud enumerations for the fireplaces."""
import logging

import httpx
from httpx import Cookies

from intellifire4py import (
    IntelliFireAPICloud,
    IntelliFireLocations,
    IntelliFireFireplaces,
)
from intellifire4py.exceptions import LoginError
from intellifire4py.model import IntelliFireUserData, IntelliFireCommonFireplaceData


class IntelliFireCloudInterface:
    """Provides a main interface to interact with the IntelliFire Cloud API, separate from individual fireplace controls.

    This class encapsulates methods to authenticate with the IntelliFire Cloud, retrieve user data, enumerate locations
    and fireplaces, and manage the user's fireplace data. It manages cloud-related operations like login, fetching
    location and fireplace details, and maintaining the state of user data.

    Attributes:
        _log (logging.Logger): Logger for the class.
        _user_data (IntelliFireUserData): Stores the user data after login.
        _cloud_fireplaces (dict[str, IntelliFireAPICloud]): Dictionary mapping fireplace identifiers to their cloud API instances.
        _is_logged_in (bool): Flag indicating whether the user is logged in.
        _cookie (httpx.Cookies): Cookies used for authenticated sessions.
        _use_http (bool): Flag to use HTTP instead of HTTPS.
        _verify_ssl (bool): Flag to enable or disable SSL verification.
    """

    _log = logging.getLogger(__name__)
    _user_data: IntelliFireUserData = IntelliFireUserData()
    _cloud_fireplaces: dict[str, IntelliFireAPICloud] = {}
    _is_logged_in = False

    def __init__(self, use_http: bool = False, verify_ssl: bool = True):
        """Initializes the IntelliFireCloudInterface with optional HTTP settings.

        Args:
            use_http (bool, optional): If True, use HTTP instead of HTTPS. Default is False.
            verify_ssl (bool, optional): If True, enable SSL certificate verification. Default is True.
        """
        self._cookie = Cookies()
        self._use_http = use_http
        self._verify_ssl = verify_ssl

        if use_http:
            self.prefix = "http"  # pragma: no cover
        else:
            self.prefix = "https"

    async def login(self, *, username: str, password: str) -> None:
        """Authenticates with the IntelliFire Cloud API using the provided username and password.

        This method performs a login operation to the cloud API, storing the session cookies
        upon successful authentication. It also triggers parsing of user data for further operations.

        Args:
            username (str): Username (typically an email) for the IntelliFire Cloud API.
            password (str): Password for the IntelliFire Cloud API.

        Raises:
            LoginError: If the login operation fails or returns an unexpected response.

        Returns:
            None
        """
        data = {"username": username, "password": password}

        # Store Username/Pass locally
        self._user_data.username = username
        self._user_data.password = password

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.prefix}://iftapi.net/a/login",
                    data=data,  # .encode(),
                )

                if response.status_code != 204:
                    raise LoginError()

                self._cookie = response.cookies
                self._user_data.parse_cookie(self._cookie)
                self._is_logged_in = True
                self._log.info("Success - Logged into IFTAPI")
                self._log.debug(f"Cookie Info: {self._cookie}")

                await self._parse_user_data(client=client)

            except LoginError as ex:
                self._log.warning("Login failure")
                raise ex
            return None

    def load_user_data(self, json_str: str) -> None:
        """Loads user data from a JSON string representation.

        This method is useful for initializing the interface with pre-existing user data
        without requiring a fresh login.

        Args:
            json_str (str): A JSON string representing user data.
        """
        self._user_data = IntelliFireUserData.model_validate_json(json_str)

    async def _login_check(self) -> None:
        """Checks if the user is currently logged in.

        Raises:
            LoginError: If the user is not logged in.
        """
        if not self._is_logged_in:
            raise LoginError("Not Logged In")

    async def _parse_user_data(self, client: httpx.AsyncClient) -> None:
        """Extracts and processes user data from the cloud API.

        This method retrieves location and fireplace details from the cloud API and constructs
        a comprehensive user data structure encompassing all necessary information for managing
        IntelliFire fireplaces.

        Args:
            client (httpx.AsyncClient): The HTTP client used for making API calls.
        """

        locations: IntelliFireLocations = await self._get_locations(client=client)

        for loc in locations.locations:
            """Enumerate the locations and start building out our user data set"""

            location_id = loc.location_id

            fireplaces: IntelliFireFireplaces = await self._get_fireplaces(
                client=client, location_id=location_id
            )

            for fireplace in fireplaces.fireplaces:
                # Construct a Cloud Fireplace so that we can poll it to construct a common fireplace
                cloud_fireplace = IntelliFireAPICloud(
                    serial=fireplace.serial,
                    use_http=self._use_http,
                    verify_ssl=self._verify_ssl,
                    cookies=self.user_data.cookies,
                )

                # Poll the fireplace
                await cloud_fireplace.poll()

                # Construct a Common Fireplace
                common_fireplace = IntelliFireCommonFireplaceData(
                    api_key=fireplace.apikey,
                    ip_address=cloud_fireplace.data.ipv4_address,
                    serial=fireplace.serial,
                    auth_cookie=self.user_data.auth_cookie,
                    user_id=self.user_data.user_id,
                    web_client_id=self.user_data.web_client_id,
                )

                self.user_data.fireplaces.append(common_fireplace)

            # # Poll to initialize all the FirePlaces
            # await asyncio.gather(
            #     *[api_cloud.poll() for api_cloud in self._cloud_fireplaces.values()]
            # )

            # Build a common fireplace

            # self._user_data.locations_with_fireplaces.append(location_with_fireplaces)

    async def _get_locations(self, client: httpx.AsyncClient) -> IntelliFireLocations:
        """Retrieves a list of locations accessible to the user from the cloud API.

        This method makes an API call to gather details about locations that the user has access to.
        The retrieved locations are used to discover fireplaces and their respective data.

        Args:
            client (httpx.AsyncClient): The HTTP client used for making the request.

        Returns:
            IntelliFireLocations: An object representing the locations accessible to the user.
        """
        await self._login_check()
        response = await client.get(url=f"{self.prefix}://iftapi.net/a/enumlocations")
        json_data = response.json()
        locations = IntelliFireLocations(**json_data)
        return locations

    async def _get_fireplaces(
        self, client: httpx.AsyncClient, *, location_id: str
    ) -> IntelliFireFireplaces:
        """Retrieves a list of fireplaces associated with a given location.

        This method queries the cloud API to obtain detailed information about fireplaces present
        at a specific location identified by the location_id.

        Args:
            client (httpx.AsyncClient): The HTTP client used for making the request.
            location_id (str): Identifier for the location whose fireplaces are to be retrieved.

        Returns:
            IntelliFireFireplaces: An object containing details of fireplaces at the specified location.
        """
        await self._login_check()
        response = await client.get(
            url=f"{self.prefix}://iftapi.net/a/enumfireplaces?location_id={location_id}"
        )
        json_data = response.json()

        fireplaces = IntelliFireFireplaces(**json_data)
        return fireplaces

    @property
    def cloud_fireplaces(self) -> list[IntelliFireAPICloud]:
        """A property that provides a list of all fireplaces across different locations.

        This property aggregates fireplaces from all locations available in the user data.

        Returns:
            list[IntelliFireFireplaceCloud]: A list of IntelliFireFireplace instances representing each fireplace.
        """
        cloud_fireplaces = [
            IntelliFireAPICloud(
                serial=common_fireplace.serial,
                cookies=common_fireplace.cookies,
                use_http=self.use_http,
                verify_ssl=self.verify_ssl,
            )
            for common_fireplace in self._user_data.fireplaces
        ]

        return cloud_fireplaces

    @property
    def use_http(self) -> bool:
        """A property that indicates whether the HTTP protocol is used instead of HTTPS.

        Returns:
            bool: True if HTTP is used, False otherwise (indicating HTTPS is used).
        """
        return self._use_http

    @property
    def verify_ssl(self) -> bool:
        """A property that indicates whether SSL verification is enabled for secure connections.

        When making HTTPS requests, SSL verification helps in ensuring the authenticity of the server's SSL certificate.

        Returns:
            bool: True if SSL verification is enabled, False otherwise.
        """
        return self._verify_ssl

    @property
    def user_data(self) -> IntelliFireUserData:
        """A property that provides access to the user's data.

        This property returns an instance of IntelliFireUserData, which contains
        information about the user, such as login credentials, user settings, and
        any other relevant data associated with the user in the context of the
        IntelliFire system. Be aware this method will also return login info.

        Returns:
            IntelliFireUserData: An object containing user-specific data.
        """

        return self._user_data
